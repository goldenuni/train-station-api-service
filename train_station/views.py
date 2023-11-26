from django.db.models import F, Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from train_station.models import (
    Station,
    Route,
    TrainType,
    Facility,
    Train,
    Crew,
    Journey,
    Order,
)
from train_station.serializers import (
    StationSerializer,
    RouteListSerializer,
    RouteSerializer,
    RouteDetailSerializer,
    TrainTypeSerializer,
    FacilitySerializer,
    TrainSerializer,
    TrainListSerializer,
    JourneySerializer,
    JourneyListSerializer,
    TrainDetailSerializer,
    JourneyDetailSerializer,
    CrewSerializer,
    CrewListSerializer,
    CrewDetailSerializer,
    OrderSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    TrainImageSerializer,
)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects
    serializer_class = TrainTypeSerializer


class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects
    serializer_class = FacilitySerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = (
        Train.objects.select_related("train_type")
        .prefetch_related("facility")
    )
    serializer_class = TrainSerializer

    @staticmethod
    def _params_to_int(qs):
        return [int(str_id) for str_id in qs.split(",")]

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer

        if self.action == "retrieve":
            return TrainDetailSerializer

        if self.action == "upload_image":
            return TrainImageSerializer

        return TrainSerializer

    def get_queryset(self):
        queryset = self.queryset
        train_type = self.request.query_params.get("train_type")
        facility = self.request.query_params.get("facility")

        if train_type:
            queryset = queryset.filter(train_type__id=str(train_type))

        if facility:
            facility_id = self._params_to_int(facility)
            queryset = queryset.filter(facility__id__in=facility_id)

        return queryset.distinct()

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific movie"""
        movie = self.get_object()
        serializer = self.get_serializer(movie, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JourneyPagePagination(PageNumberPagination):
    page_size = 5
    max_page_size = 50


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = (
        Journey.objects.
        select_related("route", "train")
        .prefetch_related("crew")
    )
    serializer_class = JourneySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer

        if self.action == "retrieve":
            return JourneyDetailSerializer

        return JourneySerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action in ("list", "retrieve"):
            queryset = queryset.annotate(
                tickets_available=F("train__cargo_num") *
                F("train__places_in_cargo")
                - Count("tickets")
            )

        return queryset


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.prefetch_related("journeys__train")
    serializer_class = CrewSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer

        if self.action == "retrieve":
            return CrewDetailSerializer

        return CrewSerializer


class OrderPagePagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects
    serializer_class = OrderSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        if self.action == "retrieve":
            return OrderDetailSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
