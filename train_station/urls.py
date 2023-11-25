from rest_framework import routers

from train_station.views import (
    StationViewSet,
    RouteViewSet,
    TrainTypeViewSet,
    FacilityViewSet,
    TrainViewSet,
    JourneyViewSet,
    CrewViewSet,
    OrderViewSet,
)

app_name = "train_station"

router = routers.DefaultRouter()
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("train-types", TrainTypeViewSet)
router.register("facilities", FacilityViewSet)
router.register("trains", TrainViewSet)
router.register("journeys", JourneyViewSet)
router.register("crews", CrewViewSet)
router.register("orders", OrderViewSet)

urlpatterns = router.urls
