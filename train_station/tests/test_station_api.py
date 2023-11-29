from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from train_station.models import Station
from train_station.serializers import StationSerializer

STATION_URL = reverse("train-station:station-list")


def detail_url(station_id: int):
    return reverse("train-station:station-detail", args=[station_id])


def sample_station(**params):
    defaults = {
        "name": "test_station",
        "latitude": 12345,
        "longitude": 12345,
    }
    defaults.update(params)

    return Station.objects.create(**defaults)


class UnauthenticatedStationApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(STATION_URL)
        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedStationApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test12345",
        )
        self.client.force_authenticate(self.user)

    def test_list_airplanes(self):
        sample_station()

        res = self.client.get(STATION_URL)

        stations = Station.objects.all()
        serializer = StationSerializer(stations, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_station_forbidden(self):
        defaults = {
            "name": "test_station",
            "latitude": 12345,
            "longitude": 12345,
        }

        res = self.client.post(STATION_URL, defaults)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminStationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com", "test12345", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_station(self):
        payload = {
            "name": "test_station",
            "latitude": 12345,
            "longitude": 12345
        }

        res = self.client.post(STATION_URL, payload)
        station = Station.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(station, key))

    def test_update_station(self):
        station = sample_station()
        payload = {"name": "testik_majestik"}
        url = detail_url(station.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_station(self):
        station = sample_station()
        url = detail_url(station.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
