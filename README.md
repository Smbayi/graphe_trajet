# 🗺️ Générateur d'Itinéraires Multimodaux Kinshasa

> **Génération de cartes interactives pour comparer les itinéraires entre le Rond Point Victoire et la Gare Centrale à Kinshasa**

Ce projet Python génère une carte interactive (`kinshasa_victoire_gare_final.html`) permettant de visualiser et comparer des itinéraires détaillés pour deux modes de transport :
- 🚗 **Voiture**
- 🚶 **Piéton**

Il s'agit d'une démonstration de l'intégration entre les services **Google Maps API** et la librairie de visualisation géographique **Folium**.

---

## 🎯 Objectif : Modélisation en Graphe Routier

### Problématique
*« Soit un véhicule qui quitte du rond-point Victoire vers la Gare centrale en passant par tous arrêts possibles. Présentez cela sous forme d'un graphe orienté dont l'état initial est ROND POINT Victoire et État final la GARE CENTRALE »*

### Solution
- **État Initial** : Rond Point Victoire
- **État Final** : Gare Centrale
- **Visualisation** : Carte interactive représentant le graphe orienté
- **Technologies** : Python + Google Maps API + Folium

---

## 🧠 Méthodologie et Architecture

Le script `trajet_kin.py` transforme une requête de navigation en graphe visuel interactif via **3 phases distinctes** :

### 📊 Flux de Données

```
Requête → API Google → Traitement Python → Visualisation Folium → Carte HTML
```

### Phase 1️⃣ : Acquisition des Données (API)

**Modélisation en Graphe Orienté**
- **Nœuds (Sommets)** : Points de départ, d'arrivée et croisements importants
- **Arêtes (Arcs)** : Segments de route avec orientation (sens uniques)
- **Poids** : Durée et distance de chaque segment
- **Algorithmes** : Dijkstra/A* pour optimisation des trajets

**APIs Utilisées :**
- Google Directions API (itinéraires)
- Google Maps Static API (vues satellites)

### Phase 2️⃣ : Traitement des Données (Python)

1. **Découpage en Segments** : Analyse des étapes (Steps) de l'API
2. **Enrichissement Visuel** : Génération d'URLs pour vues satellites
3. **Préparation Graphique** : Décodage Polyline + formatage des données

### Phase 3️⃣ : Visualisation Interactive (Folium)

1. **Tracé du Graphe** : Arêtes (lignes) + Nœuds (marqueurs)
2. **Styles Différenciés** : Pointillés pour piétons, lignes pleines pour voitures
3. **Interactivité** : Pop-ups avec instructions, distances et images satellites
4. **Export Final** : Génération du fichier HTML interactif

---

## 🚀 Structure du Projet

| Fichier | Type | Description |
|---------|------|-------------|
| `trajet_kin.py` | 🐍 **Script Python** | Code principal exécutant les 3 phases (API → Traitement → Visualisation) |
| `.env` | ⚙️ **Configuration** | Variable secrète `GOOGLE_API_KEY` |
| `kinshasa_victoire_gare_final.html` | 🌐 **Sortie HTML** | Carte interactive générée (résultat final) |

---

## 🔑 Installation et Configuration

### Prérequis
- Python 3.7+
- Compte Google Cloud avec facturation active
- Clé API Google Maps

### 1️⃣ Environnement Virtuel

```bash
# Création de l'environnement
python -m venv venv

# Activation
source venv/bin/activate      # Linux/macOS
.\venv\Scripts\activate       # Windows
```

### 2️⃣ Installation des Dépendances

```bash
pip install -r requirements.txt
```

### 3️⃣ Configuration API Google

**Créer le fichier `.env` :**
```env
GOOGLE_API_KEY="VOTRE_CLÉ_API_GOOGLE_ICI"
```

**APIs à activer dans Google Cloud Console :**
- ✅ Directions API
- ✅ Maps Static API  
- ✅ Geocoding API

---

## 🚀 Utilisation

### Exécution
```bash
python trajet_kin.py
```

### Résultat
- 📄 Génération du fichier `kinshasa_victoire_gare_final.html`
- 🌐 Ouvrir dans un navigateur
- 🎛️ Utiliser le menu pour basculer entre :
  - **Modes de transport** : Voiture / Piéton
  - **Types de vue** : Plan / Satellite

---

## 📋 Fonctionnalités

- 🗺️ **Carte Interactive** avec contrôles de navigation
- 🚗🚶 **Comparaison multimodale** (Voiture vs Piéton)
- 📍 **Marqueurs interactifs** avec pop-ups détaillés
- 🛰️ **Vues satellites** intégrées
- 📊 **Informations détaillées** : distances, durées, instructions
- 🎨 **Styles visuels différenciés** par mode de transport