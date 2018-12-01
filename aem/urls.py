from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from clients import views as client_views
from aemauthentication import views as authentication_views
from company import views as company_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Endpoint to create AEM Customer Admin
    path('users/admin/', authentication_views.RegistrationAPIView.as_view()),

    # Endpoint to create AEM Customer Engineers
    path('users/', authentication_views.CreateUserAPIView.as_view()),

    # Endpoint to authenticate all users
    path('users/login/', authentication_views.LoginAPIView.as_view(), name="login"),

    path('company/', company_views.CreateCompanyAPIView.as_view()),

    path('clients/', client_views.ClientList.as_view()),
    path('clients/<uuid:pk>/', client_views.ClientDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
