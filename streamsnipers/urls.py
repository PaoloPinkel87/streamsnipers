from django.urls import path
from .views import StreamSniperRanking


urlpatterns = [path("", StreamSniperRanking.as_view())]
