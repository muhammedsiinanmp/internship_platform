import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models import User, UserRole
from apps.internships.models import Internship
from apps.applications.models import Application


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def company_user(db):
    return User.objects.create_user(
        email="company@test.com", password="Pass123!", first_name="Co",
        last_name="Ltd", role=UserRole.COMPANY, company_name="Test Co",
    )


@pytest.fixture
def student_user(db):
    return User.objects.create_user(
        email="student@test.com", password="Pass123!", first_name="S",
        last_name="T", role=UserRole.STUDENT,
    )


@pytest.fixture
def student_user2(db):
    return User.objects.create_user(
        email="student2@test.com", password="Pass123!", first_name="S2",
        last_name="T2", role=UserRole.STUDENT,
    )


@pytest.fixture
def internship(company_user):
    return Internship.objects.create(
        company=company_user, title="Backend Intern", description="Test",
        duration_months=3, openings=2,
    )


@pytest.fixture
def student_client(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    return api_client


@pytest.fixture
def student2_client(api_client, student_user2):
    api_client.force_authenticate(user=student_user2)
    return api_client


@pytest.fixture
def company_client(api_client, company_user):
    api_client.force_authenticate(user=company_user)
    return api_client


@pytest.mark.django_db
class TestApplicationCreate:
    def test_student_can_apply(self, student_client, internship):
        response = student_client.post(
            reverse("applications:apply"),
            {"internship": str(internship.id)},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_student_cannot_apply_twice(self, student_client, internship):
        student_client.post(
            reverse("applications:apply"),
            {"internship": str(internship.id)},
            format="json",
        )
        response = student_client.post(
            reverse("applications:apply"),
            {"internship": str(internship.id)},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_two_students_can_apply_to_same_internship(
        self, student_client, student2_client, internship
    ):
        r1 = student_client.post(
            reverse("applications:apply"), {"internship": str(internship.id)}, format="json"
        )
        r2 = student2_client.post(
            reverse("applications:apply"), {"internship": str(internship.id)}, format="json"
        )
        assert r1.status_code == status.HTTP_201_CREATED
        assert r2.status_code == status.HTTP_201_CREATED

    def test_company_cannot_apply(self, company_client, internship):
        response = company_client.post(
            reverse("applications:apply"),
            {"internship": str(internship.id)},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestApplicationList:
    def test_student_sees_only_own_applications(
        self, student_client, student_user, student_user2, internship
    ):
        Application.objects.create(student=student_user, internship=internship)
        Application.objects.create(student=student_user2, internship=internship)
        response = student_client.get(reverse("applications:list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 1

    def test_company_sees_applications_for_their_internship(
        self, company_client, student_user, internship
    ):
        Application.objects.create(student=student_user, internship=internship)
        response = company_client.get(reverse("applications:list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 1
