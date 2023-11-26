from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from train_station.models import (
    Journey, Route, Train, Crew, Station, TrainType,
)
from train_station.serializers import JourneyDetailSerializer

JOURNEY_URL = reverse("train-station:journey-list")


def detail_url(journey_id: int):
    return reverse("train-station:journey-detail", args=[journey_id])


def sample_station(**params):
    defaults = {
        "name": "test_station",
        "latitude": 12345,
        "longitude": 12345,
    }
    defaults.update(params)

    return Station.objects.create(**defaults)


def sample_route(**params):
    station1 = Station.objects.create(
        name="test_station1",
        latitude=12345,
        longitude=12345,
    )

    station2 = Station.objects.create(
        name="test_station2",
        latitude=12345,
        longitude=12345,
    )

    defaults = {
        "source": station1,
        "destination": station2,
        "distance": 300,
    }

    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_train_type(**params):
    defaults = {
        "name": "test-train-type",
    }
    defaults.update(params)

    return TrainType.objects.create(**defaults)


def sample_journey(**params):
    route = Route.objects.create(
        source=sample_station(),
        destination=sample_station(),
        distance=100,
    )
    train = Train.objects.create(
        name="Test Train",
        cargo_num=50,
        places_in_cargo=25,
        train_type=sample_train_type(),
    )
    defaults = {
        "route": route,
        "train": train,
        "departure_time": "2023-09-05T18:00:00",
        "arrival_time": "2023-09-05T19:00:00",
    }
    defaults.update(params)

    return Journey.objects.create(**defaults)


def sample_crew(**params):
    defaults = {
        "first_name": "John",
        "last_name": "Doe",
        "position": "driver",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


class UnauthenticatedJourneyApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(JOURNEY_URL)
        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedJourneyApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test12345",
        )
        self.client.force_authenticate(self.user)

    def test_list_journey(self):
        sample_journey()

        res = self.client.get(JOURNEY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_journey_detail(self):
        journey = sample_journey()

        url = detail_url(journey.id)
        res = self.client.get(url)

        serializer = JourneyDetailSerializer(journey)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key in serializer.data:
            self.assertEqual(serializer.data[key], res.data[key])

    def test_create_journey_forbidden(self):
        route = Route.objects.create(
            source=sample_station(),
            destination=sample_station(),
            distance=100,
        )
        train = Train.objects.create(
            name="Test Train",
            cargo_num=50,
            places_in_cargo=25,
            train_type=sample_train_type(),
        )
        crew = sample_crew()

        defaults = {
            "route": route.id,
            "train": train.id,
            "crew": [crew.id],
            "departure_time": "2023-09-05T18:00:00",
            "arrival_time": "2023-09-05T19:00:00+",
        }

        res = self.client.post(JOURNEY_URL, defaults)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminJourneyTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com", "test12345", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_journey(self):
        route = Route.objects.create(
            source=sample_station(),
            destination=sample_station(),
            distance=100,
        )
        train = Train.objects.create(
            name="Test Train",
            cargo_num=50,
            places_in_cargo=25,
            train_type=sample_train_type(),
        )
        crew = sample_crew()

        payload = {
            "route": route.id,
            "train": train.id,
            "crew": [crew.id],
            "departure_time": "2023-09-05T18:00:00",
            "arrival_time": "2023-09-05T19:00:00",
        }

        res = self.client.post(JOURNEY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_journey(self):
        journey = sample_journey()
        payload = {
            "departure_time": "2023-09-05T20:00:00",
        }
        url = detail_url(journey.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_journey(self):
        journey = sample_journey()
        url = detail_url(journey.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
