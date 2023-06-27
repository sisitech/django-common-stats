import collections
from reports.models import ResposeType

from reports.utils import get_any_view

try:
    from core.reports_definitions import viewsDetails
except Exception as e:
    print(e)
    viewsDetails = {}


def get_response_data(model_info, response):
    # print(response)
    response_type: ResposeType = model_info.get("response_type", ResposeType.any)
    if response_type == ResposeType.any:
        return response
    data_type = type(response)
    print(data_type)

    if data_type == response_type:
        return response
    is_paginated_response = data_type == collections.OrderedDict and "count" in response
    if is_paginated_response and response_type == ResposeType.list:
        return response["results"]
    elif response_type == ResposeType.dict or response_type == ResposeType.index:
        if is_paginated_response:
            index = model_info.get("index", 0)
            results = response["results"]
            if len(results) > index:
                return results[index]
            return None
        return response
    # print("Faield zoete,,")
    return None


def get_query_parms(obj):
    query_params = {}

    if obj.start_date:
        query_params["start_date"] = obj.start_date.strftime("%Y-%m-%d")

    if obj.end_date:
        query_params["end_date"] = obj.end_date.strftime("%Y-%m-%d")

    query_params["page_size"] = obj.list_size if obj.list_size else 100
    return query_params


def get_model_info(model):
    model_info = viewsDetails.get(model, None)

    if not model_info:
        raise print(f"{model} not found for reports.")

    if "source" in model_info:
        source = model_info.get("source")
        source_model_info = viewsDetails.get(source, None)

        if not source_model_info:
            print(f"{model} source {source} not found for reports.")

        overrides = model_info.get("overrides", {})
        model_info = {**source_model_info, **overrides}
    return model_info


def get_any_stats(model="students", grouping=None, **kwargs):
    model_info = get_model_info(model)
    extra_kwargs = model_info.get("extra_kwargs", {})
    kwargs = {**kwargs, **extra_kwargs}
    # print(kwargs)

    if not grouping:
        grouping = model_info.get("grouping", "")

    ## Get filters first
    filters = model_info.get("filters", {})
    parsed_filters = {}
    for filter_key in filters:
        print("Filter ", filter_key)
        filter_info = filters[filter_key]
        filter_model_info = get_model_info(filter_info.get("source", ""))
        filter_model_info["response_type"] = ResposeType.dict
        print(kwargs.get("query_params"))
        print(filter_model_info)
        response = get_any_view(view=filter_model_info.get("view"), grouping=filter_model_info.get("grouping"), pass_grouping_kwarg="grouping" in filter_model_info, **kwargs)
        # print(response)
        mapped_response = get_response_data(filter_model_info, response)
        print(mapped_response)
        field_name = filter_info.get("field", None)
        if field_name != None and field_name in mapped_response:
            parsed_filters[filter_key] = mapped_response[field_name]
        else:
            print("Faield...")
    ## Query Params
    print(parsed_filters)
    kwargs["query_params"] = {**kwargs["query_params"], **parsed_filters}
    print(kwargs["query_params"])
    response = get_any_view(view=model_info.get("view"), grouping=grouping, pass_grouping_kwarg="grouping" in model_info, **kwargs)
    return get_response_data(model_info, response)
