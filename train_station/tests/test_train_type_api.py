from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from train_station.models import TrainType
from train_station.serializers import TrainTypeSerializer


TRAIN_TYPE_URL = reverse("train-station:traintype-list")


def detail_url(train_type_id: int):
    return reverse("train-station:traintype-detail", args=[train_type_id])


def sample_train_type(**params):
    defaults = {
        "name": "testik-majestik",
    }
    defaults.update(params)

    return TrainType.objects.create(**defaults)


class UnauthenticatedTrainTypeApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TRAIN_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainTypeApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test12345",
        )
        self.client.force_authenticate(self.user)

    def test_list_train_type(self):
        sample_train_type()

        res = self.client.get(TRAIN_TYPE_URL)

        train_type = TrainType.objects.all()
        serializer = TrainTypeSerializer(train_type, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_train_type_forbidden(self):
        defaults = {
            "name": "testik-majestik",
        }

        res = self.client.post(TRAIN_TYPE_URL, defaults)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTrainTypeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test12345",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_train_type(self):
        payload = {
            "name": "testik-majestik",
        }

        res = self.client.post(TRAIN_TYPE_URL, payload)
        train_type = TrainType.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(train_type, key))

    def test_update_train_type(self):
        train_type = sample_train_type()
        payload = {
            "name": "testik-majestik",
        }
        url = detail_url(train_type.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_train_type(self):
        train_type = sample_train_type()
        url = detail_url(train_type.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
