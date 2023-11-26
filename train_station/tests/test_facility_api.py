from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from train_station.models import Facility
from train_station.serializers import FacilitySerializer

FACILITY_URL = reverse("train-station:facility-list")


def detail_url(facility_id: int):
    return reverse("train-station:facility-detail", args=[facility_id])


def sample_facility(**params):
    defaults = {
        "name": "test-facility",
    }
    defaults.update(params)

    return Facility.objects.create(**defaults)


class UnauthenticatedFacilityApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FACILITY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFacilityApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test12345",
        )
        self.client.force_authenticate(self.user)

    def test_list_facility(self):
        sample_facility()

        res = self.client.get(FACILITY_URL)

        facilities = Facility.objects.all()
        serializer = FacilitySerializer(facilities, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_facility_forbidden(self):
        defaults = {
            "name": "test-facility",
        }

        res = self.client.post(FACILITY_URL, defaults)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminFacilityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test12345",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_facility(self):
        payload = {
            "name": "test-facility",
        }

        res = self.client.post(FACILITY_URL, payload)
        facility = Facility.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(facility, key))

    def test_update_facility(self):
        facility = sample_facility()
        payload = {
            "name": "updated-facility",
        }
        url = detail_url(facility.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_facility(self):
        facility = sample_facility()
        url = detail_url(facility.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
