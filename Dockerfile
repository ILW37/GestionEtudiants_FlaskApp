# ===== ÉTAPE 1: Image de base =====
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="votre-email@example.com"
LABEL description="Application Flask de Gestion de Diplômes NFT"
LABEL version="1.0"

# ===== ÉTAPE 2: Variables d'environnement =====
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# ===== ÉTAPE 3: Répertoire de travail =====
WORKDIR /app

# ===== ÉTAPE 4: Dépendances système =====
# Installer gcc pour certaines dépendances Python (comme web3)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ===== ÉTAPE 5: Dépendances Python =====
# Copier requirements.txt d'abord (cache Docker)
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# ===== ÉTAPE 6: Copier le code de l'application =====
COPY . .

# ===== ÉTAPE 7: Créer dossier uploads =====
RUN mkdir -p /app/uploads && chmod 777 /app/uploads

# ===== ÉTAPE 8: Script d'entrée =====
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# ===== ÉTAPE 9: Exposer le port Flask =====
EXPOSE 5000

# ===== ÉTAPE 10: Healthcheck =====
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

# ===== ÉTAPE 11: Point d'entrée et commande =====
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "app.py"]
