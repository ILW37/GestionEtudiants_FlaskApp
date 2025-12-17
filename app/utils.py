import re

def valider_adresse_ethereum(adresse):
    if not adresse:
        return False
    pattern = r'^0x[a-fA-F0-9]{40}$'
    return bool(re.match(pattern, adresse))

def valider_email(email):
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
