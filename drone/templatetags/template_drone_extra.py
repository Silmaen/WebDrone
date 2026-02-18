"""news.templatetags.template_extra"""
from django import template

register = template.Library()


@register.simple_tag
def getunit(text):
    """
    get unit symbol based on text
    """
    if text == "Prix":
        return "€"
    if text in ["Largeur", "Longueur", "Hauteur"]:
        return "mm"
    if text == "Poids":
        return "g"
    return ""


@register.filter(name='has_group')
def has_group(user, group_name):
    """
    get the belonging of a user to a group
    """
    return user.groups.filter(name=group_name).exists()
