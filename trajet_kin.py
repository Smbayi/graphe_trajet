import os
import googlemaps
import folium
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask

# =============================================================================
# 1. CONFIGURATION
# =============================================================================
load_dotenv()
API_KEY = os.getenv('GOOGLE_API_KEY')

if not API_KEY:
    raise ValueError("❌ ERREUR CRITIQUE : Clé API introuvable. Vérifiez votre fichier .env")

gmaps = googlemaps.Client(key=API_KEY)

# Définition stricte des lieux
ORIGIN = "Rond Point Victoire, Kinshasa"
DESTINATION = "Gare Centrale, Kinshasa"

# =============================================================================
# 2. FONCTIONS DE DESIGN
# =============================================================================

def get_satellite_url(lat, lng):
    """ Génère l'URL pour l'image statique dans le popup (Vue Ciel) """
    base_url = "https://maps.googleapis.com/maps/api/staticmap"
    params = f"?center={lat},{lng}&zoom=18&size=350x200&maptype=hybrid&markers=color:red|{lat},{lng}&scale=2&key={API_KEY}"
    return base_url + params

def create_popup_html(titre, instruction, distance, duree, lat, lng, couleur_bordure):
    """ Crée une belle info-bulle HTML avec image satellite """
    image_url = get_satellite_url(lat, lng)
    
    html = f"""
    <div style="font-family: 'Segoe UI', sans-serif; width: 320px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
        <div style="background-color: {couleur_bordure}; color: white; padding: 8px 12px;">
            <h5 style="margin:0; font-size:14px;">{titre}</h5>
        </div>
        <div style="background: #000;">
            <img src="{image_url}" style="width: 100%; height: 150px; object-fit: cover; opacity: 0.9;">
        </div>
        <div style="padding: 10px; background: #fff; font-size: 13px; color: #333;">
            <div style="margin-bottom: 8px;"><b>Action :</b> {instruction}</div>
            <div style="display: flex; justify-content: space-between; border-top: 1px solid #eee; padding-top: 5px; color: #666;">
                <span>📏 {distance}</span>
                <span>⏱️ {duree}</span>
            </div>
        </div>
    </div>
    """
    return html

def traiter_mode_transport(carte_folium, mode, palettes_couleurs, icone, nom_groupe, show_default=False):
    """
    Récupère les trajets pour un mode (voiture/marche) et les ajoute à la carte
    avec des couleurs différentes pour chaque alternative.
    Retourne les coordonnées précises de départ et d'arrivée du premier trajet trouvé.
    """
    print(f"   ⚡ Calcul en cours pour : {mode.upper()}...")
    
    # Création du groupe de calque (Layer)
    feature_group = folium.FeatureGroup(name=nom_groupe, show=show_default)
    
    try:
        routes = gmaps.directions(
            ORIGIN, DESTINATION, mode=mode, alternatives=True, language='fr', departure_time=datetime.now()
        )
    except Exception as e:
        print(f"   ⚠️ Erreur API ({mode}): {e}")
        return None, None

    if not routes:
        print(f"   ⚠️ Aucun trajet trouvé pour {mode}.")
        return None, None

    coords_depart_precis = None
    coords_arrivee_precis = None

    # Boucle sur les itinéraires alternatifs (Route 1, Route 2...)
    for idx, route in enumerate(routes):
        # Choix de la couleur dans la palette (cyclique)
        couleur = palettes_couleurs[idx % len(palettes_couleurs)]
        
        leg = route['legs'][0]
        summary = route.get('summary', f'Itinéraire {idx+1}')
        
        # Sauvegarde des coords précises du 1er itinéraire pour placer les drapeaux plus tard
        if idx == 0:
            coords_depart_precis = (leg['start_location']['lat'], leg['start_location']['lng'])
            coords_arrivee_precis = (leg['end_location']['lat'], leg['end_location']['lng'])

        # Décodage de la géométrie précise (Polyline)
        decoded_path = googlemaps.convert.decode_polyline(route['overview_polyline']['points'])
        path_coords = [(pt['lat'], pt['lng']) for pt in decoded_path]
        
        # Style du trait
        style_trait = {'weight': 5, 'opacity': 0.8} if mode == 'driving' else {'weight': 4, 'opacity': 0.8, 'dash_array': '5, 10'}
        
        # 1. Tracer la ligne
        folium.PolyLine(
            path_coords,
            color=couleur,
            tooltip=f"{icone} {summary} ({leg['duration']['text']})",
            **style_trait
        ).add_to(feature_group)
        
        # 2. Ajouter des points sur les étapes clés
        steps = leg['steps']
        for i, step in enumerate(steps):
            # On filtre pour ne pas surcharger la carte (seulement changements de direction majeurs)
            instr = step['html_instructions']
            if "Turn" in instr or "Tournez" in instr or "Prendre" in instr or i == 0:
                loc = step['end_location']
                popup = create_popup_html(
                    f"{icone} {summary} - Étape {i+1}", instr, 
                    step['distance']['text'], step['duration']['text'], 
                    loc['lat'], loc['lng'], couleur
                )
                
                folium.CircleMarker(
                    location=[loc['lat'], loc['lng']],
                    radius=4,
                    color=couleur,
                    fill=True,
                    fill_color='white',
                    fill_opacity=1,
                    popup=folium.Popup(popup, max_width=350)
                ).add_to(feature_group)

    # Ajouter le groupe complet à la carte principale
    feature_group.add_to(carte_folium)
    
    return coords_depart_precis, coords_arrivee_precis

# =============================================================================
# 3. MAIN
# =============================================================================

def main():
    print("🚀 DÉMARRAGE DU GÉNÉRATEUR DE TRAJET KINSHASA")
    print(f"📍 De : {ORIGIN}")
    print(f"🏁 Vers : {DESTINATION}")

    # --- A. Initialisation de la Carte ---
    # On centre sur Kinshasa par défaut
    m = folium.Map(location=[-4.325, 15.322], zoom_start=13, tiles=None)

    # --- B. Configuration des Fonds de Carte (Base Maps) ---
    # 1. Plan de ville (Par défaut)
    folium.TileLayer('OpenStreetMap', name='🗺️ Plan de Ville (Défaut)', control=True).add_to(m)
    
    # 2. Vue Satellite (Esri World Imagery - Très détaillé pour Kinshasa)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='🛰️ Vue Satellite (Ciel)',
        control=True
    ).add_to(m)

    # --- C. Calcul et Tracé des Itinéraires ---
    
    # Palettes de couleurs distinctes
    # Voiture : Rouge, Bleu foncé, Violet
    couleurs_voiture = ['#e74c3c', '#2980b9', '#8e44ad'] 
    # Marche : Vert, Orange, Turquoise
    couleurs_marche = ['#27ae60', '#d35400', '#1abc9c'] 

    # 1. Mode VOITURE (Coché par défaut)
    start_car, end_car = traiter_mode_transport(
        m, 'driving', couleurs_voiture, '🚗', "🚗 Trajets Voiture", show_default=True
    )

    # 2. Mode MARCHE (Décoché par défaut)
    start_walk, end_walk = traiter_mode_transport(
        m, 'walking', couleurs_marche, '🚶', "🚶 Trajets Piéton", show_default=False
    )

    # --- D. Placement des Marqueurs fixes (Départ / Arrivée) ---
    # On utilise les coordonnées précises récupérées du calcul voiture pour être sûr d'être sur la route
    if start_car and end_car:
        # Marqueur VICTOIRE
        folium.Marker(
            [start_car[0], start_car[1]],
            popup="<b>ROND POINT VICTOIRE</b><br>Point de Départ",
            icon=folium.Icon(color='green', icon='play', prefix='fa'),
            tooltip="Départ"
        ).add_to(m)

        # Marqueur GARE
        folium.Marker(
            [end_car[0], end_car[1]],
            popup="<b>GARE CENTRALE</b><br>Terminus",
            icon=folium.Icon(color='darkred', icon='flag', prefix='fa'),
            tooltip="Arrivée"
        ).add_to(m)

    # --- E. Contrôles et Sauvegarde ---
    # Ajout du menu de contrôle des calques (Haut Droite)
    folium.LayerControl(position='topright', collapsed=False).add_to(m)

    print("\n✅ CARTE GÉNÉRÉE !")
    print("👉 Utilisez le menu en haut à droite pour changer le fond de carte ou le mode de transport.")

    return m.get_root().render()

app = Flask(__name__)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def index():
    return main()

if __name__ == "__main__":
    app.run(debug=True)