"""Formulaire pour le drone"""
from django import forms
from .models import (
    DroneArticleComment,
    DroneComponentComment,
    DroneConfigurationComment,
    DroneFlightComment,
)


class DroneArticleCommentForm(forms.ModelForm):
    class Meta:
        model = DroneArticleComment
        fields = ('contenu',)


class DroneComponentCommentForm(forms.ModelForm):
    class Meta:
        model = DroneComponentComment
        fields = ('contenu',)


class DroneConfigurationCommentForm(forms.ModelForm):
    class Meta:
        model = DroneConfigurationComment
        fields = ('contenu',)


class DroneFlightCommentForm(forms.ModelForm):
    class Meta:
        model = DroneFlightComment
        fields = ('contenu',)
