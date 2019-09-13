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


class GenerateIndicator:
    def __init__(self, geo, session, profile, *args, **kwargs):
        self.geo = geo
        self.session = session
        self.profile = profile

    def header(self):
        """
        This will contain any information relating to noteworthy stats about the indicator.
        This must return a dictionary
        """
        return {'header': [{'title': self.profile.header,
                            'summary': self.profile.summary,
                            'info': self.disclaimer_text}]}

    def chart(self):
        """
        Details about the chart
        """
        return {'chart_title': self.profile.chart_title,
                'chart_type': self.profile.chart_type}

    def merge_parent_indicators(self, indicator_profiles):
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


    def calculation(self):
        """
        Get results for this indicator.
        """
        data, total = get_stat_data(
            [column_name],
            geo,
            session,
            table_universe=table_universe,
            table_dataset="Census and Community Survey",
            exclude_zero=exclude_zero,
        )
        return stats

    def create():
        """
        Create the dictionary containing all the details about the indicator
        """
        
    def entry(self):
        """
        main entry point to class
        """
        




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
    table_universe,
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
            table_universe=table_universe,
            table_dataset="Census and Community Survey",
            order_by="-total",
            exclude_zero=exclude_zero,
        )
    else:
        data, total = get_stat_data(
            [column_name],
            geo,
            session,
            table_universe=table_universe,
            table_dataset="Census and Community Survey",
            exclude_zero=exclude_zero,
        )

    return data, total


def get_dynamic_profiles(geo, session):
    indicator_profiles = OrderedDict(
        (p.name, []) for p in Profile.objects.order_by("display_order").all()
    )
    for i in IndicatorProfile.objects.all():
        indicator = GenerateIndicator(geo,session, i)
        indicator_profiles[i.profile.name].append(indicator)

    # Sort all the indicators for each profile
    indicator_profiles[profile.profile.name] = sorted(
                indicator_profiles[profile.profile.name],
                key=lambda profile: profile["display_order"],
            )

    # group parent and children indicators
    indicator_profiles = group_indicators(indicator_profiles)
    return indicator_profiles


    for profile in IndicatorProfile.objects.all():
        
        try:
            distribution, total = indicator_calculation(
                geo,
                session,
                column_name=profile.column_name,
                table_name=profile.table_name.name,
                table_universe=profile.universe,
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
                    "header_extra": get_total_population(geo, session),
                }
            )
    indicator_profiles = group_indicators(indicator_profiles)

    return indicator_profiles
