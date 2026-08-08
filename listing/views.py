from rest_framework.views import APIView
from .models import Listing
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import ListingSerializer
from django.contrib.postgres.search import SearchVector, SearchQuery


class ManageListingView(APIView):
    def get(self, request, format=None):
        try:
            user = request.user
            
            if not user.is_realtor:
                            return Response(
                                {'error': 'User does not have neccesary permissions for creating this listing data'},
                                status=status.HTTP_403_FORBIDDEN
                            )
                            
            slug = request.query_params.get('slug')
            
            if not slug:
                listing = Listing.objects.order_by('-date_created').filter(
                    realtor=user.email
                )
                listing = ListingSerializer(listing,many=True)
               
                return Response({'listing': listing.data},status=status.HTTP_200_OK)
           
            if not Listing.objects.filter(
                realtor=user.email,
                slug=slug
            ).exists():
                return Response({'error': 'Listing not found'},status=status.HTTP_404_NOT_FOUND)
            
            listing = Listing.objects.get(realtor=user.email,slug=slug)
            listing = ListingSerializer(listing)
            
            return Response( {'listing': listing.data}, status=status.HTTP_200_OK )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def retrieve_values(self, data):
        
        title  = data['title']
        slug  = data['slug']
        address  = data['address']
        city  = data['city']
        state  = data['state']
        zipcode  = data['zipcode']
        desription  = data['description']
        
        try: price = int(data['price'])
        except: return -1
        
        try: bedrooms = int(data['bedrooms'])
        except: return -2
        
        try: bathrooms = float(data['bathrooms'])
        except: return -3
        
        if bathrooms <= 0 or bathrooms >= 10:
            bathrooms = 1.0
        bathrooms = round(bathrooms,1)
        
        sale_type  = data['sale_type']
        if sale_type == 'FOR_RENT':
            sale_type = 'For Rent'
        else:
            sale_type = 'For Sale'
        
        home_type  = data['home_type']
        
        if home_type == 'CONDO':
            home_type = ' Condo'
        elif home_type == 'TOWNHOUSE':
            home_type = 'Townhouse'
        else:
            home_type = 'House'
        
        main_photo  = data['main_photo']
        photo_1  = data['photo_1']
        photo_2  = data['photo_2']
        photo_3  = data['photo_3']
        is_published  = data['is_published']
        
        if is_published == 'True':
            is_published = True
        else:
            is_published = False
            
        data = {
            'title': title,
            'slug': slug,
            'address': address,
            'city': city,
            'state':state,
            'zipcode':zipcode,
            'description':desription,
            'price':price,
            'bedrooms':bedrooms,
            'bathrooms':bathrooms,
            'sale_type':sale_type,
            'home_type':home_type,
            'main_photo':main_photo,
            'photo_1':photo_1,
            'photo_2':photo_2,
            'photo_3':photo_3,
            'is_published':is_published,
        }
        
    def post(self, request):
        try:
            user = request.user
            
            if not user.is_realtor:
                return Response(
                    {'error': 'User does not have neccesary permissions for creating this listing data'},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            data = request.data
            data = self.retrieve_values(data)
            
            if data == -1:
                return Response(
                            {'error': 'Price must be an number/interger'},
                            status=status.HTTP_400_BAD_REQUEST
                            )
            elif data == -2:
                return Response(
                            {'error': 'Bedrooms must be an number/interger'},
                            status=status.HTTP_400_BAD_REQUEST
                            )
            elif data == -3:
                return Response(
                                {'error': 'bathrooms must be an number/interger'},
                                status=status.HTTP_400_BAD_REQUEST
                                )
            
            if Listing.objects.filter(slug = data['slug']).exists():
                return Response(
                    {'error': 'Listing with this slug already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            Listing.objects.create(
                realtor = user.email,
                title = data['title'],
                slug = data['slug'],
                address = data['address'],
                city = data['city'],
                state = data['state'],
                zipcode = data['zipcode'],
                description = data['desription'],
                price = data['price'],
                bedrooms = data['bedrooms'],
                bathrooms = data['bathrooms'],
                sale_type = data['sale_type'],
                home_type = data['home_type'],
                main_photo = data['main_photo'],
                photo_1 = data['photo_1'],
                photo_2 = data['photo_2'],
                photo_3 = data['photo_3'],
                is_published = data['is_published'],
            )
            
            return Response(
                    {'success': 'Listing created successfully'},
                    status=status.HTTP_201_CREATED
                )
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    def put(self, request):
        try:
            user = request.user
            
            if not user.is_realtor:
                return Response(
                    {'error': 'User does not have neccesary permissions for creating this listing data'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            data = request.data
            data = self.retrieve_values(data)
            
            if data == -1:
                return Response(
                            {'error': 'Price must be an number/interger'},
                            status=status.HTTP_400_BAD_REQUEST
                            )
            elif data == -2:
                return Response(
                            {'error': 'Bedrooms must be an number/interger'},
                            status=status.HTTP_400_BAD_REQUEST
                            )
            elif data == -3:
                return Response(
                                {'error': 'bathrooms must be an number/interger'},
                                status=status.HTTP_400_BAD_REQUEST
                                )
                        
            if not Listing.objects.filter(realtor=user.email, slug = data['slug']).exists():
                return Response({'error': 'Listing does not exist'}, status=status.HTTP_404_NOT_FOUND)
            
            Listing.objects.filter(realtor=user.email, slug = data['slug']).update(
                title = data['title'],
                slug = data['slug'],
                address = data['address'],
                city = data['city'],
                state = data['state'],
                zipcode = data['zipcode'],
                description = data['desription'],
                price = data['price'],
                bedrooms = data['bedrooms'],
                bathrooms = data['bathrooms'],
                sale_type = data['sale_type'],
                home_type = data['home_type'],
                main_photo = data['main_photo'],
                photo_1 = data['photo_1'],
                photo_2 = data['photo_2'],
                photo_3 = data['photo_3'],
                is_published = data['is_published'],
            )
            
            return Response( {'success': 'Listing updated successfully'},
                            status=status.HTTP_200_OK
                            )
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    
    def patch(self, request):
        try:
            user = request.user
            
            if not user.is_realtor:
                return Response(
                    {'error': 'User does not have neccesary permissions for creating this listing data'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            data = request.data
            
            is_published = (data['is_published'].strip().title() == "True")
            
            if not Listing.objects.filter(realtor=user.email, slug=data['slug']).exists():
                return Response( {'error': 'Listing does not exist'}, status=status.HTTP_404_NOT_FOUND )
            
            Listing.objects.filter(realtor=user.email, slug=data['slug']).update( is_published = is_published )
            
            return Response( {'success': 'Listing publish updated succesfully'}, status=status.HTTP_200_OK )
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR )
    
    
    def delete(self, request):
        try:
            user = request.user
            
            if not user.is_realtor:
                return Response(
                    {'error': 'User does not have neccesary permissions for deleting this listing'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            data = request.data
            
            try: slug = data['slug']
            except: return Response({'error': 'Slug was not provided'}, status=status.HTTP_400_BAD_REQUEST )
            
            if not Listing.objects.filter(realtor=user.email, slug=data['slug']).exists():
                return Response( {'error': 'Listing you are trying to delete does not exist'}, 
                                status=status.HTTP_404_NOT_FOUND )
            
            Listing.objects.filter(realtor=user.email, slug=data['slug']).delete()
            
            if not Listing.objects.filter(realtor=user.email, slug=data['slug']).exists():
                return Response( {'success': 'Listing deleted succesfully'},status=status.HTTP_204_NO_CONTENT )
            else:
                return Response( {'error': 'Failed to delete listing'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response( {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR )
        
           
class ListingDetailView(APIView):
    def get(self, request, format=None):
        try:
            slug =  request.query_params.get('slug')
            
            if not slug: return Response({'error': 'Must provide slug'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not Listing.objects.filter(slug=slug, is_published=True):
                return Response({'error': 'Published listing with this slug does not exist'}, status=status.HTTP_404_NOT_FOUND)
            
            listing = Listing.objects.get(slug=slug, is_published=True)
            listing = ListingSerializer(listing)
            
            return Response({'listing': listing.data}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ListingsView(APIView):
    permission_classes = (permissions.AllowAny, )
    
    def get(self, request, format=None):
        try:
            if not Listing.objects.filter(is_published=True):
                return Response({'error': 'No listings in database'}, status=status.HTTP_404_NOT_FOUND)
        
            listings = Listing.objects.order_by('-date_created').filter(is_published=True)
            listings = ListingSerializer(listings, many=True)
            
            return Response(
                {'listings': listings.data}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class SearchListingView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request, format=None):
        try:
            
            city = request.query_params.get('city')
            state = request.query_params.get('state')
                    
            search = request.query_params.get('search')
            if not search : return Response({'error': 'Must pass search criteria for listings'}, status=status.HTTP_400_BAD_REQUEST )
            
            try: max_price = int(request.query_params.get('max_price'))
            except: return Response({'error': 'Max price must be an interger'}, status=status.HTTP_400_BAD_REQUEST )
            
            try: bedrooms = int(request.query_params.get('bedrooms'))
            except: return Response({'error': 'Bedrooms must be an interger'}, status=status.HTTP_400_BAD_REQUEST )
            
            try: bathrooms = float(request.query_params.get('bathrooms'))
            except: return Response({'error': 'Bathrooms must be a decimal or whole number'}, status=status.HTTP_400_BAD_REQUEST )
            
            bathrooms = 1.0 if (bathrooms < 0 or bathrooms >= 10) else bathrooms
            
            sale_type = 'For Sale' if 'sale' in request.query_params.get('sale_type').lower() else 'For Rent'
            home_type = request.query_params.get('sale_type').upper()
            home_type = 'House' if home_type == 'HOUSE' else 'Condo' if home_type == 'CONDO' else 'Townhouse'
            
            vector = SearchVector('title','desciption')
            query = SearchQuery(search)
            
            if not Listing.objects.annotate(
                search=vector
                ).filter(
                search=query,
                city=city,
                state=state,
                price__lte=max_price,
                bedrooms__gte=bedrooms,
                bathrooms__gte=bathrooms,
                sale_type=sale_type,
                home_type=home_type,
                is_published=True,
                ).exists():
                    return Response({'error': 'No listings found with this criteria'},status=status.HTTP_404_NOT_FOUND)
                
            listings = Listing.objects.annotate(
                search=vector
                ).filter(
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
                
            listings = ListingSerializer(listings, many=True)
            return Response({'listings': listings.data}, status=status.HTTP_200_OK )
            
        except Exception as e:
            return Response( {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR )