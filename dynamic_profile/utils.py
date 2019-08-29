from collections import OrderedDict
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


class GenerateIndicator:
    def __init__(self, geo, session):
        self.geo = geo
        self.session = session
        self.indicator_profiles = self.profile_order()

    def profile_order(self):
        return OrderedDict(
            (p.name, []) for p in Profile.objects.order_by("display_order").all()
        )
        

    def group_indicators(self, indicator_profiles):
        """
        We need to go through all the indicators and check whether they have a parent profile indicator.
        If they do have a parent, we need to append that indicator to the parent indicator
        We will then remove all the top level indicators that have a parent.
        """
        for profile, values in indicator_profiles.items():
            for indicator in values:
                if indicator["parent_profile"]:
                    header = indicator["parent_profile"]
                    for i in values:
                        if i["header"] == header:
                            i["has_children"] = True
                            i["children"].append(indicator)
                            break

        for profile in indicator_profiles.keys():
            indicator_profiles[profile] = [
                indicator
                for indicator in indicator_profiles[profile]
                if indicator["parent_profile"] is None
            ]

        return indicator_profiles

    def column_field_value(self, distribution, column_field=None):
        """
        Pick out a specific indicator value
        Eg: picking a specific race groups values, generally used with calculate highest.
        """
        if column_field:
            return distribution[column_field]["values"]["this"]
        return None

    def percent_total(self):
        """
        calculate the percent of a distribution over the full total.
        Eg: percentage of senior citizens to the entire population
        """
        return

    def calculation(self):
        """
        calculate the stats for an indicator.
        """
        return

    def calculate_highest(self, distribution, total, highest_type):
        """
        Calculate the highest in the distribution or the entire total of the distribution
        """
        if highest_type == "Total":
            return total
        elif highest_type == "Distribution":
            return distribution[distribution.keys()[0]]

    def generate(self, profile):
        """
        Create the indicator with all its values
        """
        try:
            distribution, total = indicator_calculation(
                    geo,
                    session,
                    column_name=profile.column_name,
                    table_name=profile.table_name.name,
                    order_by=profile.order_by,
                    exclude_zero=profile.exclude_zero,
                )
        except:
            return
        else:
            pass
            
    for profile in IndicatorProfile.objects.all():
            try:
                distribution, total = indicator_calculation(
                    geo,
                    session,
                    column_name=profile.column_name,
                    table_name=profile.table_name.name,
                    order_by=profile.order_by,
                    exclude_zero=profile.exclude_zero,
                )
            except DataNotFound as error:
                print(error)
                exit()
                indicator_profiles[profile.profile.name].append(
                    {
                        "header": profile.header,
                        "summary": profile.summary,
                        "display_order": profile.display_order,
                        "data": False,
                        "parent_profile": profile.parent_profile.header
                        if profile.parent_profile
                        else None,
                        "has_children": False,
                        "children": [],
                    }
                )
                indicator_profiles[profile.profile.name] = sorted(
                    indicator_profiles[profile.profile.name],
                    key=lambda profile: profile["display_order"],
                )
            else:
                if profile.group_remainder:
                    group_remainder(distribution, profile.group_remainder)
                indicator_profiles[profile.profile.name].append(
                    {
                        "header": profile.header,
                        "summary": profile.summary,
                        "chart_title": profile.chart_title,
                        "stat_values": distribution,
                        "total": total,
                        "distribution_maxima": calculate_highest(
                            distribution, total, profile.maximum_value
                        ),
                        "chart_type": profile.chart_type,
                        "column_field": column_field_value(
                            distribution, profile.column_field
                        ),
                        "display_order": profile.display_order,
                        "parent_profile": profile.parent_profile.header
                        if profile.parent_profile
                        else None,
                        "has_children": False,
                        "children": [],
                        "data": True,
                        "disclaimer_text": profile.disclaimer_text,
                    }
                )
                indicator_profiles[profile.profile.name] = sorted(
                    indicator_profiles[profile.profile.name],
                    key=lambda profile: profile["display_order"],
                )
        indicator_profiles = group_indicators(indicator_profiles)

        return indicator_profiles
        


def indicator_calculation(
    geo,
    session,
    column_name,
    table_name,
    order_by=False,
    percent=False,
    exclude_zero=False,
):
    """
    Get the statistics for the indicator
    """
    if order_by:
        data, total = get_stat_data(
            [column_name],
            geo,
            session,
            table_dataset="Census and Community Survey",
            order_by="-total",
            exclude_zero=exclude_zero,
        )
    else:
        data, total = get_stat_data(
            [column_name],
            geo,
            session,
            table_dataset="Census and Community Survey",
            exclude_zero=exclude_zero,
        )

    return data, total


def get_dynamic_profiles(geo, session):
    indicator_profiles = OrderedDict(
        (p.name, []) for p in Profile.objects.order_by("display_order").all()
    )
    for profile in IndicatorProfile.objects.all():
        try:
            distribution, total = indicator_calculation(
                geo,
                session,
                column_name=profile.column_name,
                table_name=profile.table_name.name,
                order_by=profile.order_by,
                exclude_zero=profile.exclude_zero,
            )
        except DataNotFound as error:
            print(error)
            exit()
            indicator_profiles[profile.profile.name].append(
                {
                    "header": profile.header,
                    "summary": profile.summary,
                    "display_order": profile.display_order,
                    "data": False,
                    "parent_profile": profile.parent_profile.header
                    if profile.parent_profile
                    else None,
                    "has_children": False,
                    "children": [],
                }
            )
            indicator_profiles[profile.profile.name] = sorted(
                indicator_profiles[profile.profile.name],
                key=lambda profile: profile["display_order"],
            )
        else:
            if profile.group_remainder:
                group_remainder(distribution, profile.group_remainder)
            indicator_profiles[profile.profile.name].append(
                {
                    "header": profile.header,
                    "summary": profile.summary,
                    "chart_title": profile.chart_title,
                    "stat_values": distribution,
                    "total": total,
                    "distribution_maxima": calculate_highest(
                        distribution, total, profile.maximum_value
                    ),
                    "chart_type": profile.chart_type,
                    "column_field": column_field_value(
                        distribution, profile.column_field
                    ),
                    "display_order": profile.display_order,
                    "parent_profile": profile.parent_profile.header
                    if profile.parent_profile
                    else None,
                    "has_children": False,
                    "children": [],
                    "data": True,
                    "disclaimer_text": profile.disclaimer_text,
                }
            )
            indicator_profiles[profile.profile.name] = sorted(
                indicator_profiles[profile.profile.name],
                key=lambda profile: profile["display_order"],
            )
    indicator_profiles = group_indicators(indicator_profiles)

    return indicator_profiles
