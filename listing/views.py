from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Listing
from .pagination import ListingPagination
from .serializers import ListingSerializer


class InvalidInput(Exception):
    """Raised when the request data is missing or malformed. Becomes a 400."""


REQUIRED_FIELDS = (
    'title', 'slug', 'address', 'city', 'state', 'zipcode', 'description',
    'price', 'bedrooms', 'bathrooms', 'sale_type', 'home_type',
    'main_photo', 'photo_1', 'photo_2', 'photo_3', 'is_published',
)


def bad_request(message):
    return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)


def not_realtor(user, action):
    """Return a 403 response if the user is not a realtor, otherwise None."""
    if user.is_realtor:
        return None
    return Response(
        {'error': f'User does not have necessary permissions for {action}'},
        status=status.HTTP_403_FORBIDDEN
    )


def validation_message(error):
    """Flatten a Django ValidationError into one readable string."""
    if hasattr(error, 'message_dict'):
        return '; '.join(
            f"{field}: {' '.join(messages)}" for field, messages in error.message_dict.items()
        )
    return ' '.join(error.messages)


class ManageListingView(APIView):
    def get(self, request, format=None):
        user = request.user
        denied = not_realtor(user, 'viewing listing data')
        if denied:
            return denied

        slug = request.query_params.get('slug')

        if not slug:
            listings = Listing.objects.order_by('-date_created').filter(realtor=user.email)
            return Response({'listing': ListingSerializer(listings, many=True).data}, status=status.HTTP_200_OK)

        try:
            listing = Listing.objects.get(realtor=user.email, slug=slug)
        except Listing.DoesNotExist:
            return Response({'error': 'Listing not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'listing': ListingSerializer(listing).data}, status=status.HTTP_200_OK)

    def retrieve_values(self, data):
        """Validate the request data and return clean values. Raises InvalidInput."""
        missing = [field for field in REQUIRED_FIELDS if field not in data]
        if missing:
            raise InvalidInput('Missing required field(s): ' + ', '.join(missing))

        try:
            price = int(data['price'])
        except (TypeError, ValueError):
            raise InvalidInput('Price must be a whole number')

        try:
            bedrooms = int(data['bedrooms'])
        except (TypeError, ValueError):
            raise InvalidInput('Bedrooms must be a whole number')

        try:
            bathrooms = float(data['bathrooms'])
        except (TypeError, ValueError):
            raise InvalidInput('Bathrooms must be a whole or decimal number')

        if bathrooms <= 0 or bathrooms >= 10:
            bathrooms = 1.0
        bathrooms = round(bathrooms, 1)

        sale_type = 'For rent' if data['sale_type'] == 'FOR_RENT' else 'For sale'

        home_type = {'CONDO': 'Condo', 'TOWNHOUSE': 'Townhouse'}.get(data['home_type'], 'House')

        return {
            'title': data['title'],
            'slug': data['slug'],
            'address': data['address'],
            'city': data['city'],
            'state': data['state'],
            'zipcode': data['zipcode'],
            'description': data['description'],
            'price': price,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'sale_type': sale_type,
            'home_type': home_type,
            'main_photo': data['main_photo'],
            'photo_1': data['photo_1'],
            'photo_2': data['photo_2'],
            'photo_3': data['photo_3'],
            'is_published': str(data['is_published']).strip().title() == 'True',
        }

    def post(self, request):
        user = request.user
        denied = not_realtor(user, 'creating listings')
        if denied:
            return denied

        try:
            values = self.retrieve_values(request.data)
        except InvalidInput as e:
            return bad_request(str(e))

        slug_taken = 'Listing with this slug already exists'
        if Listing.objects.filter(slug=values['slug']).exists():
            return bad_request(slug_taken)

        listing = Listing(realtor=user.email, **values)
        try:
            listing.full_clean()  # field lengths, choices, slug format, etc.
            listing.save()
        except ValidationError as e:
            return bad_request(validation_message(e))
        except IntegrityError:
            # Another request took the slug between our check and the save
            return bad_request(slug_taken)

        return Response({'success': 'Listing created successfully'}, status=status.HTTP_201_CREATED)

    def put(self, request):
        user = request.user
        denied = not_realtor(user, 'updating listings')
        if denied:
            return denied

        try:
            values = self.retrieve_values(request.data)
        except InvalidInput as e:
            return bad_request(str(e))

        try:
            listing = Listing.objects.get(realtor=user.email, slug=values['slug'])
        except Listing.DoesNotExist:
            return Response({'error': 'Listing does not exist'}, status=status.HTTP_404_NOT_FOUND)

        for field, value in values.items():
            setattr(listing, field, value)

        try:
            listing.full_clean()
            listing.save()
        except ValidationError as e:
            return bad_request(validation_message(e))

        return Response({'success': 'Listing updated successfully'}, status=status.HTTP_200_OK)

    def patch(self, request):
        user = request.user
        denied = not_realtor(user, 'updating listings')
        if denied:
            return denied

        data = request.data
        if 'slug' not in data or 'is_published' not in data:
            return bad_request('Must provide slug and is_published')

        is_published = str(data['is_published']).strip().title() == 'True'

        updated = Listing.objects.filter(realtor=user.email, slug=data['slug']).update(is_published=is_published)
        if not updated:
            return Response({'error': 'Listing does not exist'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'success': 'Listing publish updated succesfully'}, status=status.HTTP_200_OK)

    def delete(self, request):
        user = request.user
        denied = not_realtor(user, 'deleting listings')
        if denied:
            return denied

        if 'slug' not in request.data:
            return bad_request('Slug was not provided')

        try:
            listing = Listing.objects.get(realtor=user.email, slug=request.data['slug'])
        except Listing.DoesNotExist:
            return Response(
                {'error': 'Listing you are trying to delete does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Instance delete (not queryset delete) so the model also removes the photo files
        listing.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListingDetailView(APIView):
    def get(self, request, format=None):
        slug = request.query_params.get('slug')
        if not slug:
            return bad_request('Must provide slug')

        try:
            listing = Listing.objects.get(slug=slug, is_published=True)
        except Listing.DoesNotExist:
            return Response(
                {'error': 'Published listing with this slug does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({'listing': ListingSerializer(listing).data}, status=status.HTTP_200_OK)


class ListingsView(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, format=None):
        listings = Listing.objects.order_by('-date_created').filter(is_published=True)

        if not listings.exists():
            return Response({'error': 'No listings in database'}, status=status.HTTP_404_NOT_FOUND)

        # An out-of-range ?page= raises NotFound, which DRF turns into a 404 on its own
        paginator = ListingPagination()
        page = paginator.paginate_queryset(listings, request)

        if page is not None:
            serializer = ListingSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ListingSerializer(listings, many=True)
        return Response({'listings': serializer.data}, status=status.HTTP_200_OK)


class SearchListingView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        params = request.query_params

        search = params.get('search')
        if not search:
            return bad_request('Must pass search criteria for listings')

        city = params.get('city')
        state = params.get('state')
        if not city or not state:
            return bad_request('Must pass city and state')

        try:
            max_price = int(params.get('max_price'))
        except (TypeError, ValueError):
            return bad_request('Max price must be an integer')

        try:
            bedrooms = int(params.get('bedrooms'))
        except (TypeError, ValueError):
            return bad_request('Bedrooms must be an integer')

        try:
            bathrooms = float(params.get('bathrooms'))
        except (TypeError, ValueError):
            return bad_request('Bathrooms must be a decimal or whole number')

        bathrooms = 1.0 if (bathrooms < 0 or bathrooms >= 10) else bathrooms

        sale_type_param = params.get('sale_type')
        home_type_param = params.get('home_type')
        if not sale_type_param or not home_type_param:
            return bad_request('Must pass sale_type and home_type')

        sale_type = 'For sale' if 'sale' in sale_type_param.lower() else 'For rent'
        home_type = {'HOUSE': 'House', 'CONDO': 'Condo'}.get(home_type_param.upper(), 'Townhouse')

        # Full-text search: needs PostgreSQL
        vector = SearchVector('title', 'description')
        query = SearchQuery(search)

        listings = Listing.objects.annotate(search=vector).filter(
            search=query,
            city=city,
            state=state,
            price__lte=max_price,
            bedrooms__gte=bedrooms,
            bathrooms__gte=bathrooms,
            sale_type=sale_type,
            home_type=home_type,
            is_published=True,
        )

        if not listings.exists():
            return Response({'error': 'No listings found with this criteria'}, status=status.HTTP_404_NOT_FOUND)

        paginator = ListingPagination()
        page = paginator.paginate_queryset(listings, request)

        if page is not None:
            serializer = ListingSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ListingSerializer(listings, many=True)
        return Response({'listings': serializer.data}, status=status.HTTP_200_OK)
