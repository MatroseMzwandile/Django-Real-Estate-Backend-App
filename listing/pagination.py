from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class ListingPagination(PageNumberPagination):
    page_size = 10                       # Default items per page
    page_size_query_param = 'page_size' # Allows client to specify: ?page_size=20
    max_page_size = 100                 # Maximum limit allowed for page_size

    # Optional: If you want to keep the response key as 'listings' 
    # instead of DRF's default 'results' key:
    # def get_paginated_response(self, data):
    #     return Response({
    #         'count': self.page.paginator.count,
    #         'next': self.get_next_link(),
    #         'previous': self.get_previous_link(),
    #         'listings': data
    #     })