from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer

User = get_user_model()


class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = request.data

        try:
            name = str(data['name']).strip()
            email = str(data['email']).strip().lower()
            password = str(data['password'])
            re_password = str(data['re_password'])
        except KeyError as e:
            return Response(
                {'error': f'Missing required field: {e.args[0]}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not name:
            return Response({'error': 'Name cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(email)
        except ValidationError:
            return Response({'error': 'Enter a valid email address'}, status=status.HTTP_400_BAD_REQUEST)

        if password != re_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 8:
            return Response(
                {'error': 'Passwords must be atleast 8 characters in length'},
                status=status.HTTP_400_BAD_REQUEST
            )

        email_taken = {'error': 'User with this email already exists'}
        if User.objects.filter(email=email).exists():
            return Response(email_taken, status=status.HTTP_400_BAD_REQUEST)

        try:
            User.objects.create_user(name=name, email=email, password=password)
        except IntegrityError:
            # Two requests registered the same email at the same moment
            return Response(email_taken, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': 'User created succesfully'}, status=status.HTTP_201_CREATED)


class RetrieveUserView(APIView):
    def get(self, request, format=None):
        user = UserSerializer(request.user)
        return Response({'user': user.data}, status=status.HTTP_200_OK)
