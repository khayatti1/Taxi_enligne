# Taxi_enligne

##  Description
**Taxi_enligne** est une application web destinée à la gestion d’un service de réservation de taxis en ligne.  
Développée avec **PHP** (et potentiellement une architecture légère), elle permet aux utilisateurs de réserver un taxi facilement via une interface intuitive.

## Fonctionnalités principales
- **Réservation de taxi en ligne** : saisir un point de départ, une destination, une date et une heure pour réserver.
- **Gestion des courses** : création, affichage, modification, et suivi des réservations.
- **Interface utilisateur simple** : navigation fluide entre les sections (réservation, suivi, etc.).
- **CRUD complet** sur les entités principales (courses, clients, éventuellement chauffeurs).
- **Affichage des réservations** de manière claire pour consultation ou administration.

## Architecture & Technologies
- **Langage** : PHP  
- **Structure typique** :
  - `index.php`, `reservation.php`, ou fichiers similaires pour le routage.
  - Dossier `models/` ou un fichier pour la gestion des données (CRUD des courses).
  - Dossier `views/` ou code HTML/PHP mixte pour les pages du site.
  - Optionnel : fichier `config.php` pour les paramètres de connexion (base de données) ou d’API (ex. calcul d’itinéraire).

## Installation
1. Clonez ou téléchargez le projet :
    ```bash
    git clone https://github.com/khayatti1/Taxi_enligne.git
    ```
2. Placez le dossier du projet dans votre répertoire racine web (ex. `www/` ou `htdocs/`).
3. Configurez la base de données (MySQL/MariaDB) si une table `reservations` ou similaire est utilisée :
   - Importez un fichier SQL fourni (`taxi.sql`) ou créez la table manuellement.
4. Ajustez les paramètres de connexion à la base de données dans `config.php` (ou équivalent).
5. Lancez un serveur local (ex. **XAMPP**, **WAMP**, **Laragon** ou PHP intégré) et accédez au projet via :
    ```
    http://localhost/Taxi_enligne/
    ```

## Utilisation
- Accédez à l’application depuis votre navigateur.
- Remplissez le formulaire de réservation (départ, destination, date/heure).
- Soumettez le formulaire pour enregistrer la réservation.
- Consultez la liste des réservations existantes (confirmation, gestion).
- Modifiez ou supprimez une réservation si nécessaire (selon les fonctionnalités disponibles).

