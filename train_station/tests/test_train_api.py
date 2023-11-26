from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from train_station.models import Train, TrainType, Facility
from train_station.serializers import TrainListSerializer, TrainDetailSerializer

TRAIN_URL = reverse("train-station:train-list")


def detail_url(train_id: int):
    return reverse("train-station:train-detail", args=[train_id])


def sample_train_type(**params):
    defaults = {
        "name": "Test Train Type",
    }
    defaults.update(params)

    return TrainType.objects.create(**defaults)


def sample_facility(**params):
    defaults = {
        "name": "Test Facility",
    }
    defaults.update(params)

    return Facility.objects.create(**defaults)


def sample_train(**params):
    defaults_tt = {
        "name": "Test TrainType"
    }
    if params.get("name"):
        defaults_tt["name"] = params["name"]
    train_type = sample_train_type(**defaults_tt)
    defaults = {
        "name": "Test Train",
        "cargo_num": 100,
        "places_in_cargo": 50,
        "train_type": train_type,
    }
    defaults.update(params)

    return Train.objects.create(**defaults)


class UnauthenticatedTrainApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TRAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test12345",
        )
        self.client.force_authenticate(self.user)

    def test_list_trains(self):
        sample_train()
        train_with_facilities = sample_train(name="test1")

        facility1 = sample_facility(name="wifi")
        facility2 = sample_facility(name="WC")

        train_with_facilities.facility.add(facility1, facility2)

        res = self.client.get(TRAIN_URL)

        trains = Train.objects.all()
        serializer = TrainListSerializer(trains, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_trains_by_facility(self):
        train1 = sample_train(name="testik")
        train2 = sample_train(name="majestik")

        facility1 = sample_facility(name="wifi")
        facility2 = sample_facility(name="WC")

        train1.facility.add(facility1)
        train2.facility.add(facility2)

        train3 = sample_train(name="Train without facilities")

        res = self.client.get(TRAIN_URL, {"facility": f"{facility1.id}, {facility2.id}"})
        serializer1 = TrainListSerializer(train1)
        serializer2 = TrainListSerializer(train2)
        serializer3 = TrainListSerializer(train3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_trains_by_train_type(self):
        train1 = sample_train(name="testik")
        train2 = sample_train(name="majestik")
        train3 = sample_train()

        train_type_1 = TrainType.objects.get(id=train1.train_type.id)
        train_type_2 = TrainType.objects.get(id=train2.train_type.id)

        res = self.client.get(
            TRAIN_URL,
            {"train_type": f"{train_type_1.id}, {train_type_2.id}"}
        )

        serializer1 = TrainListSerializer(train1)
        serializer2 = TrainListSerializer(train2)
        serializer3 = TrainListSerializer(train3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_retrieve_train_detail(self):
        train = sample_train()
        train.facility.add(sample_facility(name="wifi"))

        url = detail_url(train.id)
        res = self.client.get(url)

        serializer = TrainDetailSerializer(train)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_train_forbidden(self):
        train_type = sample_train_type()

        defaults = {
            "name": "Test Train",
            "cargo_num": 100,
            "places_in_cargo": 50,
            "train_type": train_type,
        }

        res = self.client.post(TRAIN_URL, defaults)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTrainTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test12345",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_train(self):
        train_type = sample_train_type()

        payload = {
            "name": "Test Train",
            "cargo_num": 100,
            "places_in_cargo": 50,
            "train_type": train_type.id,
        }

        res = self.client.post(TRAIN_URL, payload)
        train = Train.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_train_with_facilities(self):
        facility1 = sample_facility(name="wifi")
        facility2 = sample_facility(name="WC")
        train_type = sample_train_type()

        payload = {
            "name": "Test Train",
            "cargo_num": 100,
            "places_in_cargo": 50,
            "train_type": train_type.id,
            "facility": [facility1.id, facility2.id]
        }

        res = self.client.post(TRAIN_URL, payload)
        train = Train.objects.get(id=res.data["id"])
        facilities = train.facility.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(facilities.count(), 2)
        self.assertIn(facility1, facilities)
        self.assertIn(facility2, facilities)

    def test_update_train(self):
        train = sample_train()
        payload = {
            "name": "Updated Train",
        }
        url = detail_url(train.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_train(self):
        train = sample_train()
        url = detail_url(train.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
