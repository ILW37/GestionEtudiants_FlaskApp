def get_mention(moyenne):
    """
    Calcule la mention basée sur la moyenne (sur 20).
    """
    if moyenne >= 16:
        return "Très Bien"
    elif moyenne >= 14:
        return "Bien"
    elif moyenne >= 12:
        return "Assez Bien"
    elif moyenne >= 10:
        return "Passable"
    else:
        return "Échec"
