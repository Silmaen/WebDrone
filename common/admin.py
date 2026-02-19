"""Les Pages d'admin commons"""
from django.contrib import admin
from django.utils.text import Truncator
from markdownx.admin import MarkdownxModelAdmin


class SiteArticleAdmin(admin.ModelAdmin):
    """
    Admin page for articles
    """
    list_display = (
        'titre', 'auteur', 'date', 'content_overview', 'private', 'staff')
    list_filter = ('auteur', 'date',)
    date_hierarchy = 'date'
    ordering = ('date',)
    search_fields = ('titre', 'contenu')
    prepopulated_fields = {'slug': ('titre',), }
    # Configuration du formulaire d'édition
    fieldsets = (
        # Fieldset 1 : meta-info (titre, auteur…)
        ('General', {
            'fields': ('titre', 'slug', 'auteur', 'date'),
        }),
        # Fieldset 2 : acces
        ('Acces', {
            'fields': ('private', 'superprivate', 'staff', 'developper',)
        }),
        # Fieldset 3 : contenu de l'article
        ('Content of the article', {
            'fields': ('contenu',)
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.auteur = request.user
        super().save_model(request, obj, form, change)

    def content_overview(self, article):
        """
        Retourne le texte tronqué.
        """
        return Truncator(article.contenu).chars(40, truncate='...')

    content_overview.short_description = 'content overview'


class SiteArticleCommentAdmin(MarkdownxModelAdmin):
    list_display = ('auteur', 'contenu', 'article', 'date', 'active')
    list_filter = ('auteur', 'date', 'active')
    ordering = ('article', '-date', 'auteur',)
    search_fields = ('auteur', 'contenu')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)

    def save_model(self, request, obj, form, change):
        obj.auteur = request.user
        super().save_model(request, obj, form, change)
