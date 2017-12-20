from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.players, name='players'),
    url(r'^(?P<playerid>\d{1,6})/$', views.player, name='player'),
]