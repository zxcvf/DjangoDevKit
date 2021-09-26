from django.utils.deprecation import MiddlewareMixin
from threadlocals.threadlocals import set_request_variable
from Education.db_router import DB_USING, DB_ROUTE


class SetDb(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        set_request_variable(DB_USING, view_kwargs[DB_ROUTE])
