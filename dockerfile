# Image de base
FROM python:3.10

# Répertoire de travail
WORKDIR .

# Copier les fichiers du projet dans le conteneur
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Commande pour lancer l'application
CMD ["python", "main.py"]
