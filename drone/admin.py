"""Configuration de l'administration"""
from django.contrib import admin
from .base_admin import SiteArticleAdmin, SiteArticleCommentAdmin
from .models import *


class DroneArticleAdmin(SiteArticleAdmin):
    list_display = ('titre', 'auteur', 'date', 'content_overview')
    list_filter = ('auteur', 'date',)
    date_hierarchy = 'date'
    ordering = ('date',)
    search_fields = ('titre', 'contenu')
    prepopulated_fields = {'slug': ('titre',), }
    # Configuration du formulaire d’édition
    fieldsets = (
        # Fieldset 1 : meta-info (titre, auteur…)
        ('General', {
            'fields': ('titre', 'slug', 'auteur', 'date'),
        }),
        # Fieldset 3 : contenu de l'article
        ('Content of the article', {
            'fields': ('contenu',)
        }),
    )


class DroneComponentAdmin(SiteArticleAdmin):
    list_display = ('titre', 'category')
    list_filter = ('titre', 'category')
    search_fields = ('titre', 'category')
    prepopulated_fields = {}
    fieldsets = (
        # Fieldset 1 : meta-info (titre, auteur…)
        ('General', {
            'fields': ('titre',),
        }),
        # Fieldset 2 : contenu de l'article
        ('Description du composant', {
            'fields': ('category', 'contenu', 'specs')
        }),
        # Fieldset 3 : liens
        ('Liens', {
            'fields': ('datasheet', 'photo')
        }),
    )


class DroneConfigurationAdmin(SiteArticleAdmin):
    list_display = ('version_number', 'titre', 'date', 'version_logiciel')
    list_filter = ('version_number', 'titre', 'date', 'version_logiciel')
    search_fields = ('version_number', 'titre', 'date', 'version_logiciel')
    prepopulated_fields = {}
    fieldsets = (
        # Fieldset 1 : meta-info (titre, auteur…)
        ('General', {
            'fields': ('titre', 'version_number', 'date'),
        }),
        # Fieldset 2 : contenu de l'article
        ('Description de la configuration', {
            'fields': ('contenu', 'version_logiciel')
        }),
        # Fieldset 3 : liens
        ('Liens', {
            'fields': ('Composants', 'photo')
        }),
    )


class DroneFlightAdmin(SiteArticleAdmin):
    list_display = ('titre', 'date', 'drone_configuration')
    list_filter = ('titre', 'date', 'drone_configuration')
    search_fields = ('titre', 'date', 'drone_configuration')
    prepopulated_fields = {}
    fieldsets = (
        # Fieldset 1 : meta-info (titre, auteur…)
        ('General', {
            'fields': ('titre', 'date'),
        }),
        # Fieldset 2 : contenu de l'article
        ('Description du vol', {
            'fields': ('meteo', 'contenu')
        }),
        # Fieldset 3 : liens
        ('Liens', {
            'fields': ('drone_configuration', 'datalog', 'video')
        }),
    )


admin.site.register(DroneComponentCategory)
admin.site.register(DroneArticle, DroneArticleAdmin)
admin.site.register(DroneComponent, DroneComponentAdmin)
admin.site.register(DroneConfiguration, DroneConfigurationAdmin)
admin.site.register(DroneFlight, DroneFlightAdmin)

admin.site.register(DroneArticleComment, SiteArticleCommentAdmin)
admin.site.register(DroneComponentComment, SiteArticleCommentAdmin)
admin.site.register(DroneConfigurationComment, SiteArticleCommentAdmin)
admin.site.register(DroneFlightComment, SiteArticleCommentAdmin)
