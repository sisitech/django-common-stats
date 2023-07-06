from django.http import HttpRequest

from mylib.my_common import MyCustomException


class BaseCustomReport(object):
    template = None
    export = None
    serializer_class = None

    def __init__(self, template):
        self.template = template

    def get_query_parms(self):
        obj = self.export
        query_params = {}
        if obj.start_date:
            query_params["start_date"] = obj.start_date.strftime("%Y-%m-%d")

        if obj.end_date:
            query_params["end_date"] = obj.end_date.strftime("%Y-%m-%d")

        query_params["page_size"] = obj.list_size if obj.list_size else 100
        return query_params

    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer_context(self):
        return {"query_params": self.get_query_parms()}

    def get_context(self, export):
        print("Getting context ")
        self.export = export
        serialize_class = self.get_serializer_class()
        if not serialize_class:
            raise MyCustomException("No serializer_class provided")

        print(f"Getting context serializer{serialize_class}")
        res = serialize_class(export, context=self.get_serializer_context())
        context = res.data
        print(context)

        return context


def get_any_view(view, grouping, pass_grouping_kwarg=True, is_list=True, **kwargs):
    new_request = HttpRequest()
    new_request.method = "GET"
    new_request.user = kwargs.get("user")
    new_request.META["SERVER_NAME"] = "localhost"
    new_request.META["SERVER_PORT"] = 9000
    new_request.path = f"/a/{grouping}/?hana=oiiew"
    new_request.GET = {
        **kwargs.get("query_params", {}),
        **kwargs.get("order_by", {}),
        "is_training_school": False,
    }
    other_view = view.as_view()
    view_kwargs = {}
    if pass_grouping_kwarg:
        view_kwargs = {"type": grouping}
    response = other_view(new_request, **view_kwargs)
    # print("Am done")

    data = []
    # Process the response
    if response.status_code == 200:
        # Do something with the response
        # if is_list:
        #     data = response.data["results"]
        # else:
        data = response.data

    else:
        print(response.status_code)
        print(response.data)
        data = []
        # Handle the error
    return data
