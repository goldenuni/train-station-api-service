from django.db import transaction
from rest_framework import serializers

from train_station.models import (
    Station,
    Route,
    TrainType,
    Facility,
    Train,
    Crew,
    Journey,
    Order,
    Ticket,
)


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name"
    )


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(many=False, read_only=True)
    destination = StationSerializer(many=False, read_only=True)


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ("id", "name",)


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = (
            "id", "name", "cargo_num",
            "places_in_cargo", "train_type", "facility",
        )


class TrainListSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name"
    )
    facility = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )


class TrainDetailSerializer(TrainSerializer):
    train_type = TrainTypeSerializer(many=False, read_only=True)
    facility = FacilitySerializer(many=True, read_only=False)


class JourneySerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Journey
        fields = (
            "id", "route", "train", "crew",
            "departure_time", "arrival_time"
        )


class JourneyListSerializer(JourneySerializer):
    route = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name"
    )
    train = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name",
    )
    crew = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name"
    )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "position",)


class JourneyDetailSerializer(serializers.ModelSerializer):
    route = RouteDetailSerializer(many=False, read_only=True)
    train = TrainSerializer(many=False, read_only=True)
    crew = CrewSerializer(many=True, read_only=True)
    taken_seats = serializers.SlugRelatedField(
        source="tickets",
        many=True,
        read_only=True,
        slug_field="seat"
    )

    class Meta:
        model = Journey
        fields = (
            "id", "route", "train", "taken_seats",
            "crew", "departure_time", "arrival_time"
        )


class CrewListSerializer(serializers.ModelSerializer):
    trains = serializers.SlugRelatedField(
        source="journeys",
        many=True,
        read_only=True,
        slug_field="info"
    )

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "position", "trains",)


class CrewDetailSerializer(CrewListSerializer):
    pass


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_ticket(
            cargo=attrs["cargo"],
            seat=attrs["seat"],
            train=attrs["journey"].train,
            error_to_raise=serializers.ValidationError
        )

        return data

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey")


class TicketListSerializer(TicketSerializer):
    journey = JourneyListSerializer(many=False, read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(
        many=True,
        read_only=False,
        allow_empty=False
    )

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)

            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return Order

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class OrderDetailSerializer(OrderListSerializer):
    pass
