"""Formulaire pour le drone"""
from .models import *
from markdownx.forms import forms


class DroneArticleCommentForm(forms.ModelForm):
    """
    Form for comment creation
    """
    class Meta:
        """
        Meta informations
        """
        model = DroneArticleComment
        fields = ('contenu',)


class DroneComponentCommentForm(forms.ModelForm):
    """
    Form for comment creation
    """
    class Meta:
        """
        Meta informations
        """
        model = DroneComponentComment
        fields = ('contenu',)


class DroneConfigurationCommentForm(forms.ModelForm):
    """
    Form for comment creation
    """
    class Meta:
        """
        Meta informations
        """
        model = DroneConfigurationComment
        fields = ('contenu',)


class DroneFlightCommentForm(forms.ModelForm):
    """
    Form for comment creation
    """
    class Meta:
        """
        Meta informations
        """
        model = DroneFlightComment
        fields = ('contenu',)
