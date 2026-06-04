from django.urls import path
from . import views

app_name = "internships"

urlpatterns = [
    path("", views.InternshipListCreateView.as_view(), name="list-create"),
    path("<uuid:pk>/", views.InternshipRetrieveUpdateDestroyView.as_view(), name="detail"),
]
