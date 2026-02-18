"""Quelques fonctions utiles pour la gestion des utilisateurs"""


def user_is_validated(user):
    """
    Teste si l’user est bien dans le groupe des validated
    :param user: L'user à tester
    :return: True si l’user fait bien partie des validés.
    """
    if user.is_superuser:
        return True
    if user.is_staff:
        return True
    return user.groups.filter(name="validated").exists()


def user_is_developper(user):
    """
    Teste si l’user est bien dans le groupe des validated
    :param user: L'user à tester
    :return: True si l’user fait bien partie des validés.
    """
    if user.is_superuser:
        return True
    return user.groups.filter(name="developper").exists()


def user_is_moderator(user):
    """
    Teste si l’user est bien dans le groupe des validated
    :param user: L'user à tester
    :return: True si l’user fait bien partie des validés.
    """
    if user.is_superuser:
        return True
    return user.groups.filter(name="moderator").exists()
