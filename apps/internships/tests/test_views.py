import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models import User, UserRole
from apps.internships.models import Internship, InternshipStatus


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def company_user(db):
    return User.objects.create_user(
        email="company@test.com",
        password="StrongPass123!",
        first_name="IQRAA",
        last_name="Mark",
        role=UserRole.COMPANY,
        company_name="IQRAA MARK PVT LTD",
    )


@pytest.fixture
def student_user(db):
    return User.objects.create_user(
        email="student@test.com",
        password="StrongPass123!",
        first_name="John",
        last_name="Doe",
        role=UserRole.STUDENT,
    )


@pytest.fixture
def company_client(api_client, company_user):
    api_client.force_authenticate(user=company_user)
    return api_client


@pytest.fixture
def student_client(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    return api_client


@pytest.fixture
def internship_payload():
    return {
        "title": "Backend Developer Intern",
        "description": "Work on Django REST APIs",
        "requirements": "Python, Django",
        "location": "Remote",
        "internship_type": "remote",
        "stipend_per_month": "15000.00",
        "duration_months": 3,
        "openings": 2,
        "skills_required": ["Python", "Django", "REST"],
    }


@pytest.fixture
def internship(company_user, internship_payload):
    return Internship.objects.create(
        company=company_user,
        **{k: v for k, v in internship_payload.items() if k != "stipend_per_month"},
        stipend_per_month=15000,
    )


@pytest.mark.django_db
class TestInternshipListCreate:
    def test_company_can_create_internship(self, company_client, internship_payload):
        response = company_client.post(
            reverse("internships:list-create"), internship_payload, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_student_cannot_create_internship(self, student_client, internship_payload):
        response = student_client.post(
            reverse("internships:list-create"), internship_payload, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_student_can_list_internships(self, student_client, internship):
        response = student_client.get(reverse("internships:list-create"))
        assert response.status_code == status.HTTP_200_OK

    def test_unauthenticated_cannot_list(self, api_client):
        response = api_client.get(reverse("internships:list-create"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestInternshipDetail:
    def test_company_can_update_own_internship(self, company_client, internship):
        url = reverse("internships:detail", kwargs={"pk": internship.pk})
        response = company_client.patch(url, {"title": "Updated Title"}, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_company_can_delete_own_internship(self, company_client, internship):
        url = reverse("internships:detail", kwargs={"pk": internship.pk})
        response = company_client.delete(url)
        assert response.status_code == status.HTTP_200_OK

    def test_student_cannot_delete_internship(self, student_client, internship):
        url = reverse("internships:detail", kwargs={"pk": internship.pk})
        response = student_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
