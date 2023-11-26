from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from train_station.models import Station, Route
from train_station.serializers import RouteListSerializer, RouteDetailSerializer

ROUTE_URL = reverse("train-station:route-list")


def detail_url(route_id: int):
    return reverse("train-station:route-detail", args=[route_id])


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


class UnauthenticatedRouteApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test12345",
        )
        self.client.force_authenticate(self.user)

    def test_list_routes(self):
        sample_route()

        res = self.client.get(ROUTE_URL)

        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_route_detail(self):
        route = sample_route()

        url = detail_url(route.id)
        res = self.client.get(url)

        serializer = RouteDetailSerializer(route)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route_forbidden(self):
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
            "source": station1.id,
            "destination": station2.id,
            "distance": 300,
        }

        res = self.client.post(ROUTE_URL, defaults)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test12345",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_route(self):
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

        payload = {
            "source": station1.id,
            "destination": station2.id,
            "distance": 300,
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        route = Route.objects.get(id=res.data["id"])
        stations = Station.objects.all()
        self.assertEqual(stations.count(), 2)
        self.assertIn(station1, stations)
        self.assertIn(station2, stations)


    def test_update_route(self):
        route = sample_route()
        payload = {
            "distance": "600",
        }
        url = detail_url(route.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
