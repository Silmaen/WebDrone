"""Les modèles pour le site drone"""
from django.db import models
from .base_models import SiteArticle, SiteArticleComment


class DroneArticle(SiteArticle):
    """Les articles du site de drone"""

    class Meta:
        """
        Meta data
        """
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
        #                              ground        flying
        return '<span class="mdi ' + ["mdi-download", "mdi-upload"][self.onBoard] + '"></span>'

    def render_name(self):
        stri = '<span class="mdi '
        if self.name == "Hélice":
            stri += 'mdi-fan"></span><span>Hélice</span>'
        elif self.name == "Batterie":
            stri += 'mdi-battery-outline"></span><span>Batterie</span>'
        elif self.name == "Moteur":
            stri += 'mdi-cog-outline"></span><span>Moteur</span>'
        elif self.name == "ESC (contrôleur de puissance moteur)":
            stri += 'mdi-car-cruise-control"></span><span>ESC</span>'
        elif self.name == "Caméra":
            stri += 'mdi-video-outline"></span><span>Caméra</span>'
        elif self.name == "VTX (transmetteur vidéo)":
            stri += 'mdi-video-wireless-outline"></span><span>VTX</span>'
        elif self.name == "Récepteur Vidéo":
            stri += 'mdi-camera-wireless-outline"></span><span>VRX</span>'
        elif self.name == "Télécommande":
            stri += 'mdi-controller-classic-outline"></span><span>Télécommande</span>'
        elif self.name == "Récepteur télémétrie":
            stri += 'mdi-home-thermometer-outline></span><span>Télémétrie sol</span>'
        elif self.name == "Module de radio commande":
            stri += 'mdi-antenna"></span><span>radio commande</span>'
        elif self.name == "Distributeur de puissance":
            stri += 'mdi-power-plug-outline"></span><span>Distributeur de puissance</span>'
        elif self.name == "Module de Télémétrie":
            stri += 'mdi-router-wireless"></span><span>Module Telemétrie</span>'
        elif self.name == "Controleur de vol":
            stri += 'mdi-chip"></span><span>radio commande</span>'
        elif self.name == "Cadre":
            stri += 'mdi-quadcopter"></span><span>Cadre</span>'
        else:
            stri += 'mdi-cogs"></span><span>' + str(self.name) + '</span>'
        return stri

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
        """
        Meta data for drone
        """
        verbose_name = "Composant de Drone"
        ordering = ['category', 'titre']

    def save(self, *args, **kwargs):
        """
        Surcharge de l’opérateur save pour bien définir le champ private.
        """
        self.staff = False
        self.private = False
        self.superprivate = False
        super(DroneComponent, self).save(*args, **kwargs)


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
        """
        Meta data for drone configuration
        """
        verbose_name = "Configuration Drone"
        ordering = ['-date']

    def save(self, *args, **kwargs):
        """
        Surcharge de l’opérateur save pour bien définir le champ private.
        """
        self.staff = False
        self.private = False
        self.superprivate = False
        super(DroneConfiguration, self).save(*args, **kwargs)


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
        """
        Meta data for drone
        """
        verbose_name = "Vol de  Drone"
        ordering = ['-date']

    def save(self, *args, **kwargs):
        """
        Surcharge de l’opérateur save pour bien définir le champ private.
        """
        self.staff = False
        self.private = False
        self.superprivate = False
        super(DroneFlight, self).save(*args, **kwargs)

    def render_meteo(self):
        """
        render the flight weather
        """
        ret = '<div class="meteo">\n'
        ret += '  <span class="mdi mdi-weather-windy-variant"></span>'
        ret += '  <div class="meteo_couverture">Météo: '
        if "couverture" in self.meteo:
            if self.meteo["couverture"] in ["ensoleillé", "dégagé"]:
                ret += '<span class="mdi mdi-weather-sunny"></span>\n'
            elif self.meteo["couverture"] in ["partiellement couvert"]:
                ret += '<span class="mdi mdi-weather-partly-cloudy"></span>\n'
            elif self.meteo["couverture"] in ["couvert"]:
                ret += '<span class="mdi mdi-weather-cloudy"></span>\n'
            elif self.meteo["couverture"] in ["brumeux"]:
                ret += '<span class="mdi mdi-weather-hazy"></span>\n'
            elif self.meteo["couverture"] in ["brouillard"]:
                ret += '<span class="mdi mdi-weather-fog"></span>\n'
            else:
                ret += '<span class="mdi mdi-weather-cloudy-alert">' + self.meteo["couverture"] + '</span>\n'
        else:
            ret += '<span class="mdi mdi-weather-sunny"></span>\n'
        ret += '  </div>\n'
        if "force_vent" in self.meteo:
            ret += '  <div class="meteo_force_vent"> '
            ret += '<span class="mdi mdi-weather-windy"></span>'
            ret += '<span>' + self.meteo["force_vent"] + '</span>'
            ret += '  </div>\n'
        if "direction_vent" in self.meteo:
            ret += '  <div class="meteo_direction_vent">'
            ret += '<span class="mdi mdi-compass-rose"></span>'
            ret += '<span>' + self.meteo["direction_vent"] + '</span>'
            ret += '  </div>\n'
        ret += '</div>\n'
        return ret


class DroneArticleComment(SiteArticleComment):
    """
    Classe pour les commentaires d’article
    """
    class Meta:
        """
        Meta data
        """
        verbose_name = "Commentaire d'article de drone"
        ordering = ['-date']


class DroneComponentComment(SiteArticleComment):
    """
    Classe pour les commentaires d’article
    """
    class Meta:
        """
        Meta data
        """
        verbose_name = "Commentaire de composant de drone"
        ordering = ['-date']


class DroneConfigurationComment(SiteArticleComment):
    """
    Classe pour les commentaires d’article
    """
    class Meta:
        """
        Meta data
        """
        verbose_name = "Commentaire de configuration de drone"
        ordering = ['-date']


class DroneFlightComment(SiteArticleComment):
    """
    Classe pour les commentaires d’article
    """
    class Meta:
        """
        Meta data
        """
        verbose_name = "Commentaire de vol de drone"
        ordering = ['-date']
