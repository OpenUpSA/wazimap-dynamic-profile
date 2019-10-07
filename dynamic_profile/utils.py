from collections import OrderedDict, defaultdict
from wazimap.models.data import DataNotFound
from wazimap.data.utils import (
    collapse_categories,
    calculate_median,
    calculate_median_stat,
    group_remainder,
    get_stat_data,
    percent,
    current_context,
    dataset_context,
)
from dynamic_profile.models import Profile, IndicatorProfile

MERGE_KEYS = set(["values", "numerators", "error"])


class BuildIndicator(object):
    def __init__(self, geo, session, profile, *args, **kwargs):
        self.geo = geo
        self.session = session
        self.profile = profile

    def header(self):
        """
        This will contain any information relating to noteworthy stats about the indicator.
        By default this will return the highest value with in the indicator
        """
        header = {"title": self.profile.title, "summary": self.profile.summary}
        try:
            if self.distribution:
                value = self.distribution[list(self.distribution.keys())[0]]
                header.update({"value": value["name"]})
        except AttributeError:
            header.update({"value": ""})

        return header

    def chart(self):
        """
        Details about the chart
        """
        return {
            "chart_title": self.profile.chart_title,
            "chart_type": self.profile.chart_type,
        }

    def calculation(self):
        """
        Get results for this indicator.
        """
        try:
            distribution, total = get_stat_data(
                [self.profile.field_name],
                self.geo,
                self.session,
                table_universe=self.profile.universe,
                table_dataset=self.profile.dataset,
                exclude_zero=self.profile.exclude_zero,
                percent=self.profile.percent,
                recode=self.profile.recode,
                key_order=self.profile.key_order,
                exclude=self.profile.exclude,
                order_by=self.profile.order_by,
            )
            group_remainder(distribution, self.profile.group_remainder)
            self.distribution = distribution
            return {"stat_values": distribution, "total": total}
        except DataNotFound:
            return {}

    def meta(self):
        """
        Any other information about the indicator
        """
        if self.profile.parent_profile:
            parent_profile = self.profile.parent_profile.title
        else:
            parent_profile = None

        return {
            "display_order": self.profile.display_order,
            "children": [],
            "parent_profile": parent_profile,
        }
        dicts = [self.chart(), self.calculation(), meta, self.header()]
        indicator = {}
        for d in dicts:
            indicator.update(d)
        return indicator


class BuildProfile(object):
    """
    Configure how the profile with its indicators will be built.
    """

    def __init__(self, name, geo, session):
        self.name = name
        self.geo = geo
        self.session = session
        self.indicators = []

    def create(self, cls_indicator):
        for model_indicator in IndicatorProfile.objects.filter(profile__name=self.name):
            new_indicator = cls_indicator(self.geo, self.session, model_indicator)
            self.indicators.append(new_indicator.create())
        self.sort()
        self.merge()
        return self.indicators

    def sort(self):
        """
        Sort Indicators accoring to the display_order
        """
        self.indicators = sorted(self.indicators, key=lambda i: i["display_order"])

    def merge(self):
        """
        We need to go through all the indicators and check whether they have a parent profile indicator.
        If they do have a parent, we need to append that indicator to the parent indicator
        We will then remove all the top level indicators that have a parent.
        """
        for indictor in self.indicators:
            title = indictor.get("parent_profile", None)
            if not None:
                for other in self.indicators:
                    if other["title"] == title:
                        other["children"].append(indictor)
                        break


class Section(object):
    """
    Build a section
    """

    def __init__(self, geo, session):
        self.geo = geo
        self.session = session
        self.profiles = OrderedDict(
            (p.name, []) for p in Profile.objects.order_by("display_order").all()
        )

    def build(self, cls_profile, cls_indicator):
        for profile_name in self.profiles.keys():
            profile = cls_profile(profile_name, self.geo, self.session)
            self.profiles[profile_name] = profile.create(cls_indicator)

        return self.profiles


def merge_dicts(this, other, other_key):
    """
    Recursively merges 'other' dict into 'this' dict. In particular
    it merges the leaf nodes specified in MERGE_KEYS.
    """
    for profile, indicators in this.iteritems():
        for counter, indicator in enumerate(indicators):
            if "stat_values" in indicator:
                for key, value in indicator["stat_values"].iteritems():
                    if key != "metadata":
                        try:
                            value["numerators"][other_key] = other[profile][counter][
                                "stat_values"
                            ][key]["numerators"]["this"]
                            value["values"][other_key] = other[profile][counter][
                                "stat_values"
                            ][key]["values"]["this"]
                        except KeyError:
                            value["numerators"][other_key] = None
                            value["values"][other_key] = None
