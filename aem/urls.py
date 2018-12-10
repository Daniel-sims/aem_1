from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from aemauthentication import views as authentication_views
from company import views as company_views
from clients import views as client_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # aemauthentication
    path('users/', authentication_views.CreateUserAPIView.as_view(), name="create-user"),
    path('users/login/', authentication_views.LoginAPIView.as_view(), name="login"),

    # company
    path('company/', company_views.CreateCompanyAPIView.as_view(), name="create-company"),

    # clients
    path('clients/', client_views.CreateClientAPIView.as_view(), name="create-client"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
