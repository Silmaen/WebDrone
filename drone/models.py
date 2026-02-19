"""Les modèles pour le site drone"""
from django.db import models
from .base_models import SiteArticle, SiteArticleComment


class DroneArticle(SiteArticle):
    """Les articles du site de drone"""

    class Meta:
        verbose_name = "Article du site de drone"
        ordering = ['-date']


class DroneComponentCategory(models.Model):
    """
    Class to handle component types for drones
    """
    name = models.CharField(max_length=40, verbose_name="Nom de la catégorie")
    onBoard = models.BooleanField(verbose_name="Composant volant ou restant au sol")

    def __str__(self):
        return self.name

    def render_onboard(self):
        """get icon for flying/ ground definition"""
        icon = "mdi-upload" if self.onBoard else "mdi-download"
        return f'<span class="mdi {icon}"></span>'

    def render_name(self):
        icons = {
            "Hélice": ('mdi-fan', "Hélice"),
            "Batterie": ('mdi-battery-outline', "Batterie"),
            "Moteur": ('mdi-cog-outline', "Moteur"),
            "ESC (contrôleur de puissance moteur)": ('mdi-car-cruise-control', "ESC"),
            "Caméra": ('mdi-video-outline', "Caméra"),
            "VTX (transmetteur vidéo)": ('mdi-video-wireless-outline', "VTX"),
            "Récepteur Vidéo": ('mdi-camera-wireless-outline', "VRX"),
            "Télécommande": ('mdi-controller-classic-outline', "Télécommande"),
            "Récepteur télémétrie": ('mdi-home-thermometer-outline', "Télémétrie sol"),
            "Module de radio commande": ('mdi-antenna', "radio commande"),
            "Distributeur de puissance": ('mdi-power-plug-outline', "Distributeur de puissance"),
            "Module de Télémétrie": ('mdi-router-wireless', "Module Telemétrie"),
            "Controleur de vol": ('mdi-chip', "radio commande"),
            "Cadre": ('mdi-quadcopter', "Cadre"),
        }
        if self.name in icons:
            icon, label = icons[self.name]
        else:
            icon, label = 'mdi-cogs', str(self.name)
        return f'<span class="mdi {icon}"></span><span>{label}</span>'

    def render_all(self):
        return self.render_name() + self.render_onboard()


class DroneComponent(SiteArticle):
    """
    class to handle components of drone
    """
    category = models.ForeignKey('DroneComponentCategory', on_delete=models.CASCADE,
                                 verbose_name="Catégorie")
    specs = models.JSONField(blank=True, default=dict,
                             verbose_name="Caractéristiques")
    datasheet = models.URLField(null=True, blank=True,
                                verbose_name="Liens vers la datasheet")
    photo = models.ImageField(null=True, blank=True,
                              upload_to='drone/compimg',
                              verbose_name="Photo du composant")

    class Meta:
        verbose_name = "Composant de Drone"
        ordering = ['category', 'titre']

    def save(self, *args, **kwargs):
        """
        Surcharge de l'opérateur save pour bien définir le champ private.
        """
        self.staff = False
        self.private = False
        self.superprivate = False
        super().save(*args, **kwargs)


class DroneConfiguration(SiteArticle):
    """
    class for describing drone configuration
    """
    version_number = models.CharField(max_length=10,
                                      verbose_name="Numéro de version")
    Composants = models.ManyToManyField(DroneComponent,
                                        verbose_name="Composants du drone")
    version_logiciel = models.CharField(max_length=40, blank=True, default="",
                                        verbose_name="Version du logiciel du contrôleur de vol")
    photo = models.ImageField(null=True, blank=True,
                              upload_to='drone/confimg',
                              verbose_name="Photo de la configuration")

    class Meta:
        verbose_name = "Configuration Drone"
        ordering = ['-date']

    def save(self, *args, **kwargs):
        """
        Surcharge de l'opérateur save pour bien définir le champ private.
        """
        self.staff = False
        self.private = False
        self.superprivate = False
        super().save(*args, **kwargs)


class DroneFlight(SiteArticle):
    """
    class handling drone flights
    """
    meteo = models.JSONField(blank=True, default=dict,
                             verbose_name="Definition Météo")
    drone_configuration = models.ForeignKey('DroneConfiguration', on_delete=models.CASCADE,
                                            verbose_name="la configuration de drone utilise")
    datalog = models.FileField(blank=True,
                               upload_to="drone/datalog",
                               verbose_name="lien vers le log du vol")
    video = models.FileField(blank=True,
                             upload_to="drone/videoflight",
                             verbose_name="Vidéo du vol")

    class Meta:
        verbose_name = "Vol de  Drone"
        ordering = ['-date']

    def save(self, *args, **kwargs):
        """
        Surcharge de l'opérateur save pour bien définir le champ private.
        """
        self.staff = False
        self.private = False
        self.superprivate = False
        super().save(*args, **kwargs)

    def render_meteo(self):
        """
        render the flight weather
        """
        ret = '<div class="meteo">\n'
        ret += '  <span class="mdi mdi-weather-windy-variant"></span>'
        ret += '  <div class="meteo_couverture">Météo: '
        if "couverture" in self.meteo:
            couverture = self.meteo["couverture"]
            if couverture in ["ensoleillé", "dégagé"]:
                ret += '<span class="mdi mdi-weather-sunny"></span>\n'
            elif couverture in ["partiellement couvert"]:
                ret += '<span class="mdi mdi-weather-partly-cloudy"></span>\n'
            elif couverture in ["couvert"]:
                ret += '<span class="mdi mdi-weather-cloudy"></span>\n'
            elif couverture in ["brumeux"]:
                ret += '<span class="mdi mdi-weather-hazy"></span>\n'
            elif couverture in ["brouillard"]:
                ret += '<span class="mdi mdi-weather-fog"></span>\n'
            else:
                ret += f'<span class="mdi mdi-weather-cloudy-alert">{couverture}</span>\n'
        else:
            ret += '<span class="mdi mdi-weather-sunny"></span>\n'
        ret += '  </div>\n'
        if "force_vent" in self.meteo:
            force_vent = self.meteo["force_vent"]
            ret += '  <div class="meteo_force_vent"> '
            ret += '<span class="mdi mdi-weather-windy"></span>'
            ret += f'<span>{force_vent}</span>'
            ret += '  </div>\n'
        if "direction_vent" in self.meteo:
            direction_vent = self.meteo["direction_vent"]
            ret += '  <div class="meteo_direction_vent">'
            ret += '<span class="mdi mdi-compass-rose"></span>'
            ret += f'<span>{direction_vent}</span>'
            ret += '  </div>\n'
        ret += '</div>\n'
        return ret


class DroneArticleComment(SiteArticleComment):
    """
    Classe pour les commentaires d'article
    """
    class Meta:
        verbose_name = "Commentaire d'article de drone"
        ordering = ['-date']


class DroneComponentComment(SiteArticleComment):
    """
    Classe pour les commentaires d'article
    """
    class Meta:
        verbose_name = "Commentaire de composant de drone"
        ordering = ['-date']


class DroneConfigurationComment(SiteArticleComment):
    """
    Classe pour les commentaires d'article
    """
    class Meta:
        verbose_name = "Commentaire de configuration de drone"
        ordering = ['-date']


class DroneFlightComment(SiteArticleComment):
    """
    Classe pour les commentaires d'article
    """
    class Meta:
        verbose_name = "Commentaire de vol de drone"
        ordering = ['-date']
