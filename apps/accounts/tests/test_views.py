import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models import User, UserRole


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def student_data():
    return {
        "email": "student@test.com",
        "first_name": "Test",
        "last_name": "Student",
        "role": UserRole.STUDENT,
        "password": "StrongPass123!",
        "password_confirm": "StrongPass123!",
        "university": "MIT",
    }


@pytest.fixture
def company_data():
    return {
        "email": "company@test.com",
        "first_name": "Test",
        "last_name": "Company",
        "role": UserRole.COMPANY,
        "password": "StrongPass123!",
        "password_confirm": "StrongPass123!",
        "company_name": "IQRAA MARK PVT LTD",
    }


@pytest.mark.django_db
class TestRegisterView:
    def test_student_registration_success(self, api_client, student_data):
        url = reverse("accounts:register")
        response = api_client.post(url, student_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["status"] == "success"
        assert "tokens" in data["data"]
        assert User.objects.filter(email=student_data["email"]).exists()

    def test_company_registration_success(self, api_client, company_data):
        url = reverse("accounts:register")
        response = api_client.post(url, company_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_company_registration_fails_without_company_name(self, api_client, company_data):
        company_data.pop("company_name")
        url = reverse("accounts:register")
        response = api_client.post(url, company_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_fails_password_mismatch(self, api_client, student_data):
        student_data["password_confirm"] = "WrongPassword!"
        url = reverse("accounts:register")
        response = api_client.post(url, student_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_email_registration_fails(self, api_client, student_data):
        url = reverse("accounts:register")
        api_client.post(url, student_data, format="json")
        response = api_client.post(url, student_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginView:
    def test_login_success(self, api_client, student_data):
        # Register first
        api_client.post(reverse("accounts:register"), student_data, format="json")
        login_data = {"email": student_data["email"], "password": student_data["password"]}
        response = api_client.post(reverse("accounts:login"), login_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.json()["data"]

    def test_login_wrong_password(self, api_client, student_data):
        api_client.post(reverse("accounts:register"), student_data, format="json")
        response = api_client.post(
            reverse("accounts:login"),
            {"email": student_data["email"], "password": "wrong"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestProfileView:
    def test_get_profile_authenticated(self, api_client, student_data):
        reg_response = api_client.post(
            reverse("accounts:register"), student_data, format="json"
        )
        token = reg_response.json()["data"]["tokens"]["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = api_client.get(reverse("accounts:profile"))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["email"] == student_data["email"]

    def test_get_profile_unauthenticated(self, api_client):
        response = api_client.get(reverse("accounts:profile"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
