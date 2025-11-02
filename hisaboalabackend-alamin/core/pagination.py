from rest_framework.pagination import PageNumberPagination

class DefaultPagination(PageNumberPagination):
    page_size = 20               # default page size
    page_size_query_param = "page_size"  # client can override
    max_page_size = 100          # prevent abuse
