import logging

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
    merge_dicts,
)
from census.profile import find_dicts_with_key
from census.utils import get_ratio
from wazimap.geo import geo_data
from itertools import repeat
from dynamic_profile.models import Profile, IndicatorProfile

MERGE_KEYS = set(["values", "numerators", "error"])
log = logging.getLogger(__name__)


def enhance_api_data(api_data):
    dict_list = find_dicts_with_key(api_data, "values")
    for d in dict_list:
        raw = {}
        enhanced = {}
        geo_value = d["values"]["this"]
        num_comparatives = 2

        # create our containers for transformation
        for obj in ["values", "error", "numerators", "numerator_errors"]:
            if obj not in d:
                raw[obj] = dict(zip(geo_data.comparative_levels, repeat(0)))
            else:
                raw[obj] = d[obj]
            enhanced[obj] = OrderedDict()
        enhanced["index"] = OrderedDict()
        enhanced["error_ratio"] = OrderedDict()
        comparative_sumlevs = []
        for sumlevel in geo_data.comparative_levels:
            # add the index value for comparatives
            if sumlevel in raw["values"]:
                enhanced["values"][sumlevel] = raw["values"][sumlevel]
                enhanced["index"][sumlevel] = get_ratio(
                    geo_value, raw["values"][sumlevel]
                )
                # add to our list of comparatives for the template to use
                if sumlevel != "this":
                    comparative_sumlevs.append(sumlevel)

            # add the moe ratios
            if (sumlevel in raw["values"]) and (sumlevel in raw["error"]):
                enhanced["error"][sumlevel] = raw["error"][sumlevel]
                enhanced["error_ratio"][sumlevel] = get_ratio(
                    raw["error"][sumlevel], raw["values"][sumlevel], 3
                )

            # add the numerators and numerator_errors
            if sumlevel in raw["numerators"]:
                enhanced["numerators"][sumlevel] = raw["numerators"][sumlevel]

            if (sumlevel in raw["numerators"]) and (
                sumlevel in raw["numerator_errors"]
            ):
                enhanced["numerator_errors"][sumlevel] = raw["numerator_errors"][
                    sumlevel
                ]

            if len(enhanced["values"]) >= (num_comparatives + 1):
                break
        # replace data with enhanced version
        for obj in [
            "values",
            "index",
            "error",
            "error_ratio",
            "numerators",
            "numerator_errors",
        ]:
            d[obj] = enhanced[obj]

    return api_data


class BuildIndicator(object):
    def __init__(self, geo, session, profile, *args, **kwargs):
        self.geo = geo
        self.session = session
        self.profile = profile

    def context_comparative_geo(self, comp_geo):
        """
        Calculte the dataset_context stat_data for a comparative geo.
        """
        with dataset_context(year=str(self.profile.dataset_context)):
            try:
                distribution, total = get_stat_data(
                    [self.profile.field_name],
                    comp_geo,
                    self.session,
                    table_name=self.profile.table_name.name,
                    exclude_zero=self.profile.exclude_zero,
                    percent=self.profile.percent,
                    recode=self.profile.recode,
                    key_order=self.profile.key_order,
                    exclude=self.profile.exclude,
                    order_by=self.profile.order_by,
                )
                return distribution
            except DataNotFound:
                return {}

    def comparative_geo(self, geo, header=False):
        """
        calculate the stat data for comparative geos
        """
        distribution, total = get_stat_data(
            [self.profile.field_name],
            geo,
            self.session,
            table_name=self.profile.table_name.name,
            exclude_zero=self.profile.exclude_zero,
            percent=self.profile.percent,
            recode=self.profile.recode,
            key_order=self.profile.key_order,
            exclude=self.profile.exclude,
            order_by=self.profile.order_by,
        )
        if header:
            return total
        return distribution

    def header_compare_geos(self):
        values = {}
        comparative_geos = geo_data.get_comparative_geos(self.geo)
        for comp_geo in comparative_geos:
            values.update(
                {
                    "{}".format(comp_geo.geo_level): self.comparative_geo(
                        comp_geo, header=True
                    )
                }
            )
        return values

    def compare_geos(self):
        """
        Get the values for the comparative geo and add it to the main geo
        "Note": for land cover we dont have provincial or country, need to skip these for
        comparative geo.
        """
        comparative_geos = geo_data.get_comparative_geos(self.geo)
        for comp_geo in comparative_geos:
            try:
                if self.profile.dataset_context:
                    if comp_geo.geo_level not in ("country", "province"):
                        merge_dicts(
                            self.distribution,
                            self.context_comparative_geo(comp_geo),
                            comp_geo.geo_level,
                        )
                else:
                    merge_dicts(
                        self.distribution,
                        self.comparative_geo(comp_geo),
                        comp_geo.geo_level,
                    )
            except KeyError:
                log.error("Unbale to merge dicts")
                pass

    def header(self):
        """
        This will contain any information relating to noteworthy stats about the indicator.
        By default this will return the highest value with in the indicator
        results = 'text|number|percent'
        """

        header = {
            "title": self.profile.title,
            "info": self.profile.info,
            "result": {
                "config": True,
                "type": "name",
                "name": "",
                "summary": self.profile.summary,
                "stat_data": {},
            },
            "extra_results": [],
        }
        try:
            if self.distribution:
                if self.profile.header_result == "distribution_total":
                    stat_values = {"this": self.total}
                    stat_values.update(self.header_compare_geos())
                    header["result"]["stat_data"]["values"] = stat_values
                    header["result"]["stat_data"]["summary"] = self.profile.summary
                    header["result"]["stat_data"]["name"] = self.profile.summary
                    header["result"]["type"] = "number"
                elif self.profile.header_result == "highest_percent":
                    stat_data = self.distribution[self.profile.header_field]
                    header["result"]["type"] = "percentage"
                    header["result"]["stat_data"] = stat_data
                    header["result"]["stat_data"]["type"] = "percentage"
                    header["result"]["stat_data"]["summary"] = self.profile.summary
                elif self.profile.header_result == "highest_category":
                    stat_data = self.distribution[list(self.distribution.keys())[0]]
                    header["result"]["stat_data"] = stat_data
                    header["result"]["stat_data"]["type"] = "name"
                    header["result"]["stat_data"]["summary"] = self.profile.summary

        except (AttributeError, DataNotFound, KeyError):
            pass

        header = enhance_api_data(header)

        return header

    def chart(self):
        """
        Details about the chart
        """
        return {
            "chart_title": self.profile.chart_title,
            "chart_type": self.profile.chart_type,
            "chart_design": self.profile.chart_design,
        }

    def dataset_context_stat_data(self):
        """
        Calulate data with should have a particular context
        """
        with dataset_context(year=str(self.profile.dataset_context)):
            try:
                self.distribution, self.total = get_stat_data(
                    [self.profile.field_name],
                    self.geo,
                    self.session,
                    table_name=self.profile.table_name.name,
                    exclude_zero=self.profile.exclude_zero,
                    percent=self.profile.percent,
                    recode=self.profile.recode,
                    key_order=self.profile.key_order,
                    exclude=self.profile.exclude,
                    order_by=self.profile.order_by,
                )
                self.compare_geos()

                if self.profile.group_remainder:
                    group_remainder(self.distribution, self.profile.group_remainder)

                self.distribution = enhance_api_data(self.distribution)
                return {"stat_values": self.distribution}
            except DataNotFound:
                return {}

    def stat_data(self):
        try:
            self.distribution, self.total = get_stat_data(
                [self.profile.field_name],
                self.geo,
                self.session,
                table_name=self.profile.table_name.name,
                exclude_zero=self.profile.exclude_zero,
                percent=self.profile.percent,
                recode=self.profile.recode,
                key_order=self.profile.key_order,
                exclude=self.profile.exclude,
                order_by=self.profile.order_by,
            )
            self.compare_geos()
            if self.profile.group_remainder:
                group_remainder(self.distribution, self.profile.group_remainder)

            self.distribution = enhance_api_data(self.distribution)
            return {"stat_values": self.distribution}
        except (DataNotFound, KeyError):
            return {}

    def calculation(self):
        """
        Get results for this indicator.
        """

        if self.profile.dataset_context:
            return self.dataset_context_stat_data()
        else:
            return self.stat_data()

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

    def create(self):
        """
        Create the dictionary containing all the details about the indicator
        """
        dicts = [self.chart(), self.meta(), self.calculation(), self.header()]
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
        for model_indicator in IndicatorProfile.objects.filter(
            profile__name=self.name
        ).filter(geo_level__contains=[self.geo.geo_level]):
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
        We need to go through all the indicators and check whether they have a parent indicator.
        If they do have a parent, we need to append that indicator to the parent indicator
        We will then remove all the top level indicators that have a parent.
        """
        for indicator in self.indicators:
            title = indicator.get("parent_profile", None)
            if not None:
                for other in self.indicators:
                    if other["title"] == title:
                        other["children"].append(indicator)
                        other["extra_results"].append(indicator["result"])
                        break
        self.indicators = [
            indictor for indictor in self.indicators if not indictor["parent_profile"]
        ]


class Section(object):
    """
    Build a section
    """

    def __init__(self, geo, session):
        self.geo = geo
        self.session = session
        self.profiles = OrderedDict(
            (p.name, [])
            for p in Profile.objects.filter(
                geo_level__contains=[self.geo.geo_level]
            ).order_by("display_order")
        )

    def build(self, cls_profile, cls_indicator):
        for profile_name in self.profiles.keys():
            profile = cls_profile(profile_name, self.geo, self.session)
            self.profiles[profile_name] = profile.create(cls_indicator)

        return self.profiles


# def merge_dicts(this, other, other_key):
#     """
#     Recursively merges 'other' dict into 'this' dict. In particular
#     it merges the leaf nodes specified in MERGE_KEYS.
#     """
#     for profile, indicators in this.items():
#         for counter, indicator in enumerate(indicators):
#             if "stat_values" in indicator:
#                 for key, value in indicator["stat_values"].items():
#                     if key != "metadata":
#                         try:
#                             value["numerators"][other_key] = other[profile][counter][
#                                 "stat_values"
#                             ][key]["numerators"]["this"]
#                             value["values"][other_key] = other[profile][counter][
#                                 "stat_values"
#                             ][key]["values"]["this"]
#                         except KeyError:
#                             value["numerators"][other_key] = None
#                             value["values"][other_key] = None
