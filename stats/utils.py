from functools import reduce
from operator import le
import operator
from django.db.models import Count, Q

from mylib.my_common import MyCustomException, str2bool
from core.model_definitions import models_definitions


def get_model_stats_definitions(model_name):
    return models_definitions[model_name]


def get_formatted_filter_set(stat_type_stats_definition, kwargs):
    print("Got formatted filterset")
    # print(kwargs["query_params"])
    query_params = kwargs["query_params"]
    filters = kwargs.get("filters")
    stat_type = kwargs.get("stat_type")
    formatted = {"{}__{}".format(ft, filters.get(ft)["lookup_expr"]): "{}".format(filters.get(ft)["value"]) for ft in filters}

    enabled_filters = get_enabled_filters(stat_type_stats_definition, stat_type, kwargs, query_params=query_params)  # stat_definition.get("enabled_filters", None)
    if enabled_filters:
        formatted = {**formatted, **enabled_filters}
    # print(stat_type)
    # print(enabled_filters)
    return formatted


def get_enabled_filters(stats_definitions, stat_type, kwargs, query_params=None):
    """
    Get default filters

    "enabled_filters": {
            "is_training_school": {
                "field_name": "stream__school__is_training_school",
                "value": False,
            },
        }
    """
    # print("Got the folowin query params")
    # print(query_params)
    stat_definition = stats_definitions[stat_type]

    model_name = kwargs.get("model_name")

    model_definition = get_model_stats_definitions(model_name)
    default_model_filters = model_definition.get("default_filters", None)
    # print(default_model_filters)
    enabled_filters = stat_definition.get("enabled_filters", {})
    # print(default_model_filters)
    # print(stats_definitions)

    for key in default_model_filters:
        # print(key)
        filter = default_model_filters[key]
        query_value = query_params.get(key, None)
        default_value = filter.get("value")

        if type(default_value) == bool and query_value != None:
            query_value = str2bool(query_value)

        # print(f"Query value {query_value} ")
        enabled_filters[filter.get("field_name")] = query_value or default_value

    # print(enabled_filters)

    if len(enabled_filters.keys()) == 0:
        return None

    return enabled_filters


def get_order_by_default_field(kwargs):
    if kwargs.get("stat_type") == "id":
        return "id"
    return "value"


def my_order_by(queryset, kwargs):
    order = kwargs.get("query_params").get("order", None)
    order_by = kwargs.get("query_params").get("order_by", None)
    order_by_field = get_order_by_default_field(kwargs)
    if order_by:
        order_by_field = order_by
    if order:
        if order.lower() == "asc":
            return queryset.order_by(order_by_field)
        elif order.lower() == "desc":
            return queryset.order_by("-{}".format(order_by_field))
    return queryset.order_by(order_by_field)


def get_group_by(stats_definitions, kwargs):
    stat_type = kwargs.get("stat_type")
    if stat_type not in stats_definitions or "value" not in stats_definitions[stat_type]:
        raise MyCustomException("{} not configure properly", stat_type)
    return stats_definitions[stat_type]["value"]


def get_resp_fields(stats_definitions, kwargs):
    stat_type = kwargs.get("stat_type")
    fields = {}
    if stat_type in stats_definitions and "resp_fields" in stats_definitions[stat_type]:
        fields = stats_definitions[stat_type].get("resp_fields", {})
    else:
        fields = kwargs.get("default_fields", {})

    fields[kwargs.get("count_name")] = Count(
        "id",
    )

    # Consider only resp or default fields for the `only_and_filter_field`
    only_and_filter_fields = getonly_and_filter_fields(kwargs)
    if len(only_and_filter_fields) > 0:
        return_fields = {}
        for field in only_and_filter_fields:
            if fields.get(field, None) != None:
                return_fields[field] = fields.get(field, None)
        if return_fields == {}:
            return fields
        return return_fields

    return fields


# def get_only_filter_field()


def get_comparison_fields(stats_definitions, kwargs):
    stat_type = kwargs.get("stat_type")
    export = kwargs.get("export", False)

    export_only_fields = stats_definitions[stat_type].get("export_only_fields", {})

    if kwargs.get("stat_type") == "id":
        id_fields = {**stats_definitions[stat_type]["extra_fields"]}
        if export:
            return {**id_fields, **export_only_fields}
        return id_fields

    annotate_fields = {}
    if stat_type not in stats_definitions or "extra_fields" not in stats_definitions[stat_type]:
        annotate_fields = get_resp_fields(stats_definitions, kwargs)
    else:
        annotate_fields = {**stats_definitions[stat_type]["extra_fields"], **get_resp_fields(stats_definitions, kwargs)}

    if export:
        return {**annotate_fields, **export_only_fields}
    return annotate_fields


def get_annotate_resp_fields(stats_definitions, kwargs):
    stat_type = kwargs.get("stat_type")
    return_type = kwargs.get("return_type")
    if kwargs.get("stat_type") == "id":
        export = kwargs.get("export", False)
        export_only_fields = stats_definitions[stat_type].get("export_only_fields", {})

        resp_fields = stats_definitions[stat_type].get("resp_fields", {})
        all_resp_fields = [*[field for field in {**stats_definitions[stat_type]["extra_fields"]}], *[field for field in resp_fields]]
        if export:
            return [*all_resp_fields, *[field for field in export_only_fields]]
        return all_resp_fields

    return ["value", *[field for field in get_comparison_fields(stats_definitions, kwargs)]]


def getonly_and_filter_fields(kwargs):
    try:
        return kwargs.get("array_query_params").getlist("only_and_filter_field")
    except Exception as e:
        return []


def get_grouped_by_data(queryset, stats_definitions, kwargs):
    if kwargs.get("stat_type") == "id":
        # Rely on default field for the list in case of any only_and_filter_field fields active
        annotate_fields = kwargs.get("default_fields", {})
    else:
        annotate_fields = get_comparison_fields(stats_definitions, kwargs)
    filters = []
    # annotate_fields = get_comparison_fields(stats_definitions, kwargs)
    ## Check to see if any filters returned from comparison_fields
    # print(annotate_fields.get(only_and_filter_field, None))

    only_and_filter_fields = getonly_and_filter_fields(kwargs)
    valid_only_filter_fields = []
    if len(only_and_filter_fields) > 0:
        for field_name in only_and_filter_fields:
            field = annotate_fields.get(field_name, None)
            if field != None:
                field_filter = getattr(field, "filter")
                filters.append(field_filter)
                valid_only_filter_fields.append(field_name)
    if len(filters) == 1:
        att = queryset.filter(*filters)
    elif len(filters) > 1:
        # print("More than one")
        filter_query = reduce(operator.or_, (f_filter for f_filter in filters))
        # print(filter_query)
        att = queryset.filter(filter_query)  # .filter(*filters)
    else:
        att = queryset

    # print("****")
    # print(kwargs.get("stat_type"), kwargs.get("export"))
    # print(list((key for key in get_annotate_resp_fields(stats_definitions, kwargs))))
    if kwargs.get("stat_type") == "id":
        att = att.annotate(value=get_group_by(stats_definitions, kwargs)).annotate(**get_comparison_fields(stats_definitions, kwargs)).values(*get_annotate_resp_fields(stats_definitions, kwargs))
        return att

    stat_type = kwargs.get("stat_type")

    values = ("value",)
    stat_definition = stats_definitions[stat_type]
    # print(stat_definition)

    # if "grouping" in stat_definition:
    #     print(stat_definition["grouping"])
    #     values = stat_definition["grouping"]

    # print(values)
    att = (
        att.annotate(value=get_group_by(stats_definitions, kwargs))
        .values(
            *values,
        )
        .annotate(**annotate_fields)
        .values(*get_annotate_resp_fields(stats_definitions, kwargs))
    )
    return att
