from django.urls import path
from . import views

app_name = "applications"

urlpatterns = [
    path("", views.ApplicationListView.as_view(), name="list"),
    path("apply/", views.ApplicationCreateView.as_view(), name="apply"),
    path("<uuid:pk>/", views.ApplicationDetailView.as_view(), name="detail"),
]
