"""Fichier main.urls.py définissant les urls."""
from django.conf.urls.static import static
from django.conf import settings as main_settings
from django.urls import path
from .views import (
    index,
    detailed_article,
    vols,
    detailed_vol,
    configurations,
    detailed_configuration,
    composants,
    detailed_composant,
)


urlpatterns = [
    path("", index, name='index'),
    path('drone/', index, name='index1'),
    path('news/<int:article_id>', detailed_article, name='detailed_article'),
    path('vols', vols, name='vols'),
    path('vols/<int:vol_id>', detailed_vol, name='detailed_vols'),
    path('confs', configurations, name='confs'),
    path('confs/<int:conf_id>', detailed_configuration, name='detailed_confs'),
    path('comps', composants, name='comps'),
    path('comps/<int:comp_id>', detailed_composant, name='detailed_comps'),
]
