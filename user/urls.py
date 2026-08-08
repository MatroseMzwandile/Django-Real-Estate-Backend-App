from .views import RegisterView, RetrieveUserView
from django.urls import path

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('me', RetrieveUserView.as_view()),
]