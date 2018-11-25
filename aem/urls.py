from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from clients import views as client_views
from aemauthentication import views as authentication_views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('user/', authentication_views.UserRetrieveUpdateAPIView.as_view()),
    path('users/', authentication_views.RegistrationAPIView.as_view()),
    path('users/login/', authentication_views.LoginAPIView.as_view()),

    path('clients/', client_views.ClientList.as_view()),
    path('clients/<uuid:pk>/', client_views.ClientDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
