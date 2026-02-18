"""Modèles communs à toutes les apps"""
from django.conf import settings
from django.db import models
from django.utils import timezone
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from django.utils.text import Truncator


truncation = 200  # Longueur de la troncature dans les articles
comment_truncation = 100  # Longueur de la troncature dans les commentaires
nb_last_comments = 3  # Le nombre de commentaires à renvoyer en mode tronqué


class SiteArticle(models.Model):
    """
    Objet de manipulation des articles
    """
    titre = models.CharField(
        max_length=100,
        verbose_name="Titre de l'article")
    slug = models.SlugField(
        max_length=100,
        verbose_name="slug de l'article")
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name="Auteur de l'article")
    contenu = MarkdownxField(
        blank=True, default="",
        verbose_name="Contenu de l'article au format Markdown")
    date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date de parution")
    private = models.BooleanField(
        default=False,
        verbose_name="Nécessite un utilisateur pour être vu")
    superprivate = models.BooleanField(
            default=False,
            verbose_name="Nécessite un utilisateur validé ou l'auteur pour être vu")
    staff = models.BooleanField(
        default=False,
        verbose_name="Nécessite un utilisateur du staff ou l'auteur pour être vu")
    developper = models.BooleanField(
            default=False,
            verbose_name="Nécessite un utilisateur 'développeur' pour être vu")

    def contenu_md(self):
        """
        Rendu tronqué du contenu markdown.
         :return : La sortie html.
        """
        return Truncator(markdownify(str(self.contenu))).chars(truncation, truncate='...', html=True)

    def contenu_all_md(self):
        """
        Rendu complet du contenu markdown.
         :return : La sortie html.
        """
        return markdownify(str(self.contenu))

    def nb_comments(self):
        """
        Obtient le nombre de commentaires associés à l’article.
         :return : Nombre de commentaires.
        """
        return len(self.get_all_comments())

    def get_comments(self):
        """
        Fonction qui renvoie les `nb_last_comments` derniers commentaires.
         :return : Les nb_last_comments derniers commentaires.
        """
        return self.get_all_comments()[:nb_last_comments]

    def get_all_comments(self):
        """
        Renvoie la liste de tous les commentaires.
         :return : Tous les commentaires
        """
        return self.comments.filter(active=True).order_by("-date")

    def save(self, *args, **kwargs):
        """
        Surcharge de l’opérateur save pour bien définir le champ private.
        """
        if self.staff or self.developper:
            self.private = True
            self.superprivate = True
        elif self.superprivate:
            self.private = True
        super(SiteArticle, self).save(*args, **kwargs)

    class Meta:
        """
        Meta data
        """
        verbose_name = "article"
        ordering = ['-date']

    def __str__(self):
        return self.titre


class SiteArticleComment(models.Model):
    """
    Objet de stockage des commentaires
    """
    article = models.ForeignKey(
        SiteArticle, on_delete=models.CASCADE,
        verbose_name="Article lié",
        related_name="comments")
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, editable=False, on_delete=models.CASCADE,
        verbose_name="Auteur du commentaire")
    contenu = MarkdownxField(
        blank=True, default="",
        verbose_name="Contenu du commentaire au format Markdown")
    date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date de parution")
    active = models.BooleanField(
        default=False)

    def contenu_md(self):
        """
        Rendu tronqué du contenu markdown.
         :return : La sortie html.
        """
        return Truncator(markdownify(str(self.contenu))).chars(comment_truncation, truncate='...', html=True)

    def contenu_all_md(self):
        """
        Rendu complet du contenu markdown.
         :return : La sortie html.
        """
        return markdownify(str(self.contenu))

    class Meta:
        """
        Meta data
        """
        verbose_name = "Commentaire d'article"
        ordering = ['-date']

    def __str__(self):
        return str(self.auteur) + "_" + str(self.date)
