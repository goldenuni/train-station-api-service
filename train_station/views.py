from rest_framework import viewsets

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
    queryset = Train.objects
    serializer_class = TrainSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer

        if self.action == "retrieve":
            return TrainDetailSerializer

        return TrainSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects
    serializer_class = JourneySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer

        if self.action == "retrieve":
            return JourneyDetailSerializer

        return JourneySerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.prefetch_related("journeys__train")
    serializer_class = CrewSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer

        if self.action == "retrieve":
            return CrewDetailSerializer

        return CrewSerializer


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
