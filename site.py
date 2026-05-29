import streamlit as st
import json
import os
from datetime import datetime
import time
import pandas as pd
import base64
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
import numpy as np

# ==========================================
# 0. CONFIGURATION & THÈME CSS (HYPERPOP + MATRIX)
# ==========================================
st.set_page_config(page_title="Prédictions", page_icon="🔮", layout="centered", initial_sidebar_state="expanded")

def injecter_design():
    st.markdown("""
    <style>
/* ==========================================
        /* 0. ÉRADICATION DU BLANC/GRIS & VOYAGE SPATIAL OPTIMISÉ
        /* ========================================== */
        
        /* On force le fond sombre à la racine et sur le header */
        :root, body, [data-testid="stHeader"] {
            background-color: #090014 !important;
        }
        
        /* TEXTES NORMAUX (ANTI-GRIS FONCÉ ABSOLU) */
        p, span, label, li, .stMarkdown, .stText, div[data-testid="stMarkdownContainer"] * {
            color: #e0f7fa !important;
            font-family: 'Verdana', sans-serif !important;
        }
        
        /* Ciel étoilé Cyberpunk - OPTIMISÉ ANTI-LAG (Seulement 3 couches légères) */
        .stApp {
            background-color: #090014 !important;
            background-image: 
                radial-gradient(circle at 20% 30%, #ffffff 1.5px, transparent 1.5px),
                radial-gradient(circle at 70% 80%, #00ffff 2px, transparent 2px),
                radial-gradient(circle at 40% 10%, #ff00ff 1.5px, transparent 1.5px) !important;
            background-size: 100px 100px !important;
            /* Animation plus lente (40s) pour soulager la carte graphique */
            animation: voyage-spatial-opti 40s linear infinite !important;
        }
        
        /* On lève le rideau noir pour voir les étoiles */
        [data-testid="stAppViewContainer"], .main, .block-container {
            background-color: transparent !important;
        }
        
        @keyframes voyage-spatial-opti {
            0% { background-position: 0px 0px; }
            100% { background-position: 100px 100px; }
        }

        /* LA CORRECTION MAGIQUE 2 : FORCE LA COULEUR DES ONGLETS PARTOUT */
        /* L'astérisque * cible TOUS les sous-éléments cachés par Streamlit */
        div[role="radiogroup"] label, div[role="radiogroup"] label * {
            color: #00ffff !important; 
            font-weight: 900 !important;
        }
        div[role="radiogroup"] label[data-checked="true"], div[role="radiogroup"] label[data-checked="true"] * {
            color: #ffff00 !important; 
        }

        /* 1. FIX DÉFINITIF DES MENUS DÉROULANTS */
        [data-baseweb="popover"], [data-baseweb="popover"] > div, 
        [role="listbox"], [role="option"], ul[role="listbox"], [data-baseweb="menu"] {
            background-color: #050010 !important; border: 2px solid #ff00ff !important; color: #00ffff !important;
        }
        [role="listbox"] li, [role="option"] {
            background-color: #050010 !important; color: #00ffff !important; font-family: 'Courier New', monospace !important; font-weight: bold !important; transition: all 0.2s ease !important;
        }
        [role="listbox"] li:hover, [role="option"]:hover, [role="listbox"] li[aria-selected="true"], [role="option"][aria-selected="true"] {
            background-color: #ff00ff !important; color: #ffff00 !important;
        }
        [role="option"] div, [role="option"] span { color: inherit !important; }

        /* TITRES */
        h1, h2, h3, h4 {
            font-family: 'Arial Black', Impact, sans-serif !important; font-style: italic !important; color: #ffffff !important; text-transform: uppercase !important;
            text-shadow: 1px 1px 0px rgba(255, 0, 255, 0.5), -1px -1px 0px rgba(0, 255, 255, 0.5) !important; letter-spacing: 1px !important; margin-bottom: 10px !important; transition: all 0.3s ease;
        }
        h1:hover, h2:hover, h3:hover, h4:hover { text-shadow: 4px 4px 0px #ff00ff, -4px -4px 0px #00ffff !important; transform: skew(-3deg); }

        /* MENU LATÉRAL */
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child { background-color: #050010 !important; border-right: 4px solid #39ff14 !important; }

        /* MENU DE NAVIGATION */
        div[role="radiogroup"] { flex-direction: row !important; gap: 10px !important; flex-wrap: wrap !important; margin-bottom: 20px !important; }
        div[role="radiogroup"] > label > div:first-child { display: none !important; }
        div[role="radiogroup"] > label {
            background-color: #12003b !important; border: 3px solid #ff00ff !important; color: #00ffff !important; padding: 10px 15px !important; font-weight: 900 !important; text-transform: uppercase !important; cursor: pointer !important; transition: all 0.2s ease !important;
        }
        div[role="radiogroup"] > label:hover { border-color: #00ffff !important; box-shadow: 0 0 15px rgba(0, 255, 255, 0.6) !important; transform: translateY(-2px); color: #ffffff !important; }
        div[role="radiogroup"] > label[data-checked="true"] { background-color: #ff00ff !important; color: #ffff00 !important; border-color: #00ffff !important; box-shadow: 0 0 15px #ff00ff, 0 0 10px #00ffff !important; transform: scale(1.05); }

        /* INPUTS */
        div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > textarea, input, textarea, div[data-baseweb="select"] > div {
            background-color: #000000 !important; color: #00ffff !important; -webkit-text-fill-color: #00ffff !important; border: 2px solid #00ffff !important; border-radius: 0px !important; font-family: 'Courier New', monospace !important; font-weight: bold !important;
        }

        /* BOUTONS D'ACTION */
        .stButton>button, [data-testid="stSidebar"] button {
            background-color: #00ffff !important; color: #000000 !important; border: 4px solid #ff00ff !important; font-family: 'Arial Black', sans-serif !important; font-size: 1.1rem !important; text-transform: uppercase !important; box-shadow: 5px 5px 0px #ff00ff !important; transition: all 0.2s ease !important; width: 100% !important;
        }
        .stButton>button div p, [data-testid="stSidebar"] button div p { color: #000000 !important; font-weight: 900 !important; }
        .stButton>button:active, .stButton>button:hover, [data-testid="stSidebar"] button:hover { transform: translate(5px, 5px) !important; box-shadow: 0px 0px 0px #ff00ff !important; background-color: #ffff00 !important; border-color: #39ff14 !important; }

        /* JAUGES DE CRÉDENCE */
        div[data-testid="stTickBar"] { background: linear-gradient(90deg, #ff00ff 0%, #00ffff 100%) !important; height: 12px !important; border-radius: 6px !important; box-shadow: 0 0 15px rgba(0, 255, 255, 0.8) !important; }
        div[data-baseweb="slider"] div[role="slider"] { background-color: #ffff00 !important; border: 4px solid #fff !important; border-radius: 0 !important; width: 26px !important; height: 26px !important; box-shadow: 0 0 15px #ffff00, 0 0 25px #00ffff !important; }

        /* CONTENEURS & EXPANDERS */
        div[data-testid="stForm"], div[data-testid="stExpander"] { background-color: rgba(20, 0, 40, 0.9) !important; border: 3px solid #00ffff !important; box-shadow: 5px 5px 0px #ff00ff !important; padding: 15px !important; }
        div[data-testid="stExpander"] summary p { font-family: 'Arial Black', sans-serif !important; color: #ffff00 !important; font-size: 1.1rem !important; }

        /* METRICS */
        div[data-testid="stMetricValue"] { color: #ffff00 !important; text-shadow: 2px 2px 0px #ff00ff !important; font-family: 'Arial Black', sans-serif !important; font-style: italic !important; }

        /* TABLEAU */
        .hyper-table { width: 100%; border-collapse: collapse; font-family: 'Verdana', sans-serif; background-color: #000; border: 3px solid #ff00ff; }
        .hyper-table th { background: #00ffff; color: #000; padding: 12px; text-transform: uppercase; font-weight: 900; }
        .hyper-table td { padding: 10px; color: #39ff14; border-bottom: 2px dashed #ff00ff; font-weight: bold; }

        /* CSS DU CHAT (DÉBAT MATRICIEL) */
        .chat-container { background: rgba(0,0,0,0.6); padding: 10px; border-left: 4px solid #00ffff; border-radius: 0 10px 10px 0; margin-bottom: 8px; font-family: 'Courier New', monospace; box-shadow: inset 0 0 10px rgba(0,255,255,0.1); }
        .chat-user { color: #ff00ff; font-weight: bold; font-size: 1.1rem; text-shadow: 0 0 5px #ff00ff; }
        .chat-msg { color: #fff; margin-left: 10px; }

        /* ==========================================
        /* ANIMATIONS DOPAMINE (NOTIFS, JAUGE V4)
        /* ========================================== */
        .ball-broken { font-size: 6rem; text-align: center; animation: shatter 0.8s steps(4) forwards; text-shadow: 0 0 30px rgba(255,0,0,0.8); }
        @keyframes shatter { 0% { transform: scale(1); filter: grayscale(0); } 50% { transform: scale(1.2) rotate(5deg); filter: hue-rotate(90deg); } 100% { transform: scale(0.9) rotate(-10deg); filter: grayscale(1) contrast(0.5); opacity: 0.6; } }
        .ball-fade { font-size: 6rem; text-align: center; animation: blink-out 1.5s ease-in-out infinite alternate; }
        @keyframes blink-out { 0% { opacity: 1; filter: drop-shadow(0 0 20px #ff00ff); } 100% { opacity: 0.2; filter: drop-shadow(0 0 0px transparent); } }
        .ball-glow { font-size: 6rem; text-align: center; animation: hyper-glow 0.5s ease-in-out infinite alternate; }
        @keyframes hyper-glow { 0% { filter: drop-shadow(0 0 10px #00ffff); transform: scale(1); } 100% { filter: drop-shadow(0 0 35px #ff00ff) drop-shadow(0 0 10px #ffff00); transform: scale(1.1); } }
        .third-eye-psy { font-size: 7rem; text-align: center; animation: psy-pulse 0.3s linear infinite; }
        @keyframes psy-pulse { 0% { transform: scale(1) rotate(0deg); filter: hue-rotate(0deg) drop-shadow(0 0 20px #39ff14); } 50% { transform: scale(1.3) rotate(5deg); filter: hue-rotate(180deg) drop-shadow(0 0 40px #ff00ff); } 100% { transform: scale(1) rotate(-5deg); filter: hue-rotate(360deg) drop-shadow(0 0 20px #00ffff); } }
        .reward-card { background: linear-gradient(135deg, #15002a 0%, #000000 100%) !important; border: 4px solid #ffff00 !important; box-shadow: 0 0 40px rgba(255, 0, 255, 0.6) !important; padding: 30px !important; text-align: center; margin-bottom: 20px; }
        .xp-bar-container { width: 100%; height: 35px; background: linear-gradient(90deg, #ff0055 0%, #ffff00 50%, #39ff14 100%); border: 3px solid #ff00ff; border-radius: 17px; position: relative; overflow: hidden; margin: 15px 0; box-shadow: 0 0 15px rgba(255, 0, 255, 0.4); }
        .xp-bar-overlay { position: absolute; right: 0; top: 0; height: 100%; background: #090014; border-left: 2px solid rgba(255,255,255,0.4); }
        .sparks-front { position: absolute; left: -2px; top: -5px; height: 45px; width: 4px; background: #ffffff; box-shadow: 0 0 10px #ffffff, 0 0 20px #ffff00, -5px 0 30px #ff00ff; z-index: 5; }
        .sparks-front::before, .sparks-front::after { content: ''; position: absolute; top: 50%; left: 0; width: 4px; height: 4px; border-radius: 50%; background: transparent; }
        .sparks-front::before { animation: explode-1 0.4s infinite ease-out; }
        .sparks-front::after { animation: explode-2 0.6s infinite ease-out; animation-delay: 0.2s; }
        @keyframes explode-1 { 0% { box-shadow: 0 0 2px #fff, 0 0 2px #fff, 0 0 2px #fff, 0 0 2px #fff, 0 0 2px #fff; opacity: 1; } 100% { box-shadow: -30px -12px 4px #ffff00, -45px 10px 2px #39ff14, -20px 15px 3px #ff00ff, -50px -5px 4px #00ffff, -15px -15px 2px #ffffff; opacity: 0; } }
        @keyframes explode-2 { 0% { box-shadow: 0 0 2px #fff, 0 0 2px #fff, 0 0 2px #fff, 0 0 2px #fff; opacity: 1; } 100% { box-shadow: -25px 14px 4px #ff0055, -35px -12px 3px #ffff00, -55px 5px 2px #39ff14, -20px -8px 4px #ffffff; opacity: 0; } }
        .zoom-pop-text { animation: zoomPop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; opacity: 0; transform: scale(0.2); margin-bottom: 10px; }
        .delay-1 { animation-delay: 0.3s; } .delay-2 { animation-delay: 0.8s; } .delay-3 { animation-delay: 5.0s; }
        @keyframes zoomPop { 0% { opacity: 0; transform: scale(0.2); } 100% { opacity: 1; transform: scale(1); } }
        .flying-points { position: fixed; z-index: 10000; font-family: 'Arial Black', sans-serif; font-weight: 900; font-size: 5rem; color: #39ff14; text-shadow: 0 0 20px #39ff14, 0 0 40px #ffff00; pointer-events: none; animation: fly-to-score 1.5s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; }
        @keyframes fly-to-score { 0% { top: 50%; left: 50%; transform: translate(-50%, -50%) scale(0); opacity: 0; } 15% { top: 50%; left: 50%; transform: translate(-50%, -50%) scale(1.2); opacity: 1; } 30% { top: 50%; left: 50%; transform: translate(-50%, -50%) scale(1); opacity: 1; } 100% { top: 10%; left: 10%; transform: translate(0, 0) scale(0.3); opacity: 0; } }

        /* CHEMIN DE PROGRESSION SIDEBAR V2 (PRO) */
        .progress-wrapper { margin: 25px 0 15px 0; font-family: 'Verdana', sans-serif; }
        .progress-track { position: relative; width: 100%; height: 8px; background: #1a0033; border-radius: 4px; box-shadow: inset 0 0 5px #000; }
        .progress-fill { position: absolute; top: 0; left: 0; height: 100%; background: linear-gradient(90deg, #ff00ff, #ffd700); border-radius: 4px; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 0 10px #ffd700; }
        .nodes-container { position: absolute; top: -6px; left: 0; width: 100%; height: 100%; display: flex; justify-content: space-between; align-items: center; pointer-events: none; }
        .node-wrapper { display: flex; flex-direction: column; align-items: center; position: relative; }
        .node { width: 16px; height: 16px; border-radius: 50%; background: #333; border: 2px solid #ff00ff; z-index: 2; transition: all 0.5s ease; }
        .node.active { background: #ffd700; border-color: #ffffff; box-shadow: 0 0 15px #ffd700, 0 0 5px #ffffff; transform: scale(1.2); }
        .node-label { position: absolute; top: 22px; font-size: 0.65rem; color: #666; font-weight: bold; text-transform: uppercase; white-space: nowrap; transition: all 0.3s ease; }
        .node-wrapper.active .node-label { color: #ffd700; text-shadow: 0 0 5px rgba(255, 215, 0, 0.6); }

        .custom-success-anim { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); font-family: 'Arial Black', sans-serif !important; font-size: 3rem; font-style: italic; font-weight: 900; color: #ffff00; text-align: center; z-index: 9999; pointer-events: none; background: rgba(0, 0, 0, 0.95); padding: 20px 40px; border: 5px solid #ff00ff; box-shadow: 0 0 50px #ff00ff, inset 0 0 20px #00ffff; animation: pop-glitch 1.2s cubic-bezier(0.1, 0.9, 0.2, 1) forwards; }
        @keyframes pop-glitch { 0% { transform: translate(-50%, -50%) scale(0.5); opacity: 0; } 20% { transform: translate(-50%, -50%) scale(1.1); opacity: 1; text-shadow: 5px 0 #ff00ff; } 40% { transform: translate(-50%, -50%) scale(1); text-shadow: -5px 0 #00ffff; } 80% { transform: translate(-50%, -50%) scale(1); opacity: 1; } 100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; } }
        /* ==========================================
        /* CSS AVATAR PIXEL ART
        /* ========================================== */
        .avatar-pixel {
            width: 40px;
            height: 40px;
            border: 2px solid #00ffff;
            border-radius: 5px;
            image-rendering: pixelated; /* Empêche le flou ! */
            box-shadow: 0 0 10px #ff00ff;
            vertical-align: middle;
            margin-right: 10px;
        }
        /* ==========================================
        /* ANTIDOTE : FIX DES ICÔNES STREAMLIT (Flèches, Croix)
        /* ========================================== */
        span.material-symbols-rounded, 
        span[data-testid="stIconMaterial"], 
        i.material-icons,
        .st-icon {
            font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
            color: inherit !important;
        }
    </style>
    """, unsafe_allow_html=True)

injecter_design()

def trigger_animation(message, jouer_son=False):
    if jouer_son:
        jouer_son_invisible("validation.mp3") # Lancement du son
        
    st.markdown(f"<div class='custom-success-anim'>✨ {message} ✨</div>", unsafe_allow_html=True)
    time.sleep(1.3) # On attend 1.3 secondes pour que le son ait le temps de se faire entendre
    rafraichir()

def rafraichir():
    try: st.rerun()
    except AttributeError: st.experimental_rerun()

def jouer_son_invisible(nom_fichier):
    """Injecte un lecteur audio invisible en HTML qui se lance tout seul"""
    try:
        with open(nom_fichier, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(f'<audio autoplay="true" style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except Exception as e:
        pass # Si le fichier MP3 n'est pas trouvé, le code ne plantera pas

# ==========================================
# 1. GESTION BDD (VIA GITHUB GIST - LA MATRICE)
# ==========================================
import requests

def charger_joueurs():
    # On lit les identifiants depuis le coffre-fort (st.secrets)
    return dict(st.secrets["joueurs"])

def get_github_headers():
    # Les entêtes d'autorisation pour hacker la Matrice
    return {
        "Authorization": f"token {st.secrets['bdd']['github_token']}",
        "Accept": "application/vnd.github.v3+json"
    }

def load_data():
    gist_id = st.secrets["bdd"]["gist_id"]
    url = f"https://api.github.com/gists/{gist_id}"
    try:
        response = requests.get(url, headers=get_github_headers())
        response.raise_for_status() # Vérifie que la requête a fonctionné
        gist_data = response.json()
        content = gist_data["files"]["base_de_donnees_hyper.json"]["content"]
        return json.loads(content)
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données : {e}")
        # Base de secours si GitHub est en carafe
        return {"utilisateurs": {}, "questions": [], "paris": []}

def save_data(data):
    gist_id = st.secrets["bdd"]["gist_id"]
    url = f"https://api.github.com/gists/{gist_id}"
    payload = {
        "files": {
            "base_de_donnees_hyper.json": {
                "content": json.dumps(data, indent=4)
            }
        }
    }
    try:
        requests.patch(url, headers=get_github_headers(), json=payload)
    except Exception as e:
        st.error(f"Échec de la sauvegarde dans la Matrice : {e}")

def init_db(joueurs_autorises):
    global db # On manipule la variable globale chargée
    modifie = False
    
    # MAJ Structure Utilisateurs (avec support Avatar)
    for nom in joueurs_autorises.keys():
        if nom not in db["utilisateurs"]:
            db["utilisateurs"][nom] = {"score": 0, "historique_vu": [], "badges": [], "gains_historique": [], "avatar": None}
            modifie = True
        else:
            if "badges" not in db["utilisateurs"][nom]: db["utilisateurs"][nom]["badges"] = []; modifie = True
            if "gains_historique" not in db["utilisateurs"][nom]: db["utilisateurs"][nom]["gains_historique"] = []; modifie = True
            if "avatar" not in db["utilisateurs"][nom]: db["utilisateurs"][nom]["avatar"] = None; modifie = True
            
    # MAJ Structure Questions
    for q in db["questions"]:
        if "commentaires" not in q: q["commentaires"] = []; modifie = True
        
    if modifie:
        save_data(db)

# Lancement de la connexion
joueurs_autorises = charger_joueurs()
db = load_data()
init_db(joueurs_autorises)

def obtenir_rang(score):
    if score < 100: return "Débutant 🌙"
    elif score < 300: return "Initié 🔮"
    elif score < 600: return "Expert ⚡"
    else: return "Oracle 🌐"


# ==========================================
# 2. ÉCRAN DE CONNEXION
# ==========================================
if "utilisateur_courant" not in st.session_state: st.session_state.utilisateur_courant = None
if "page_actuelle" not in st.session_state: st.session_state.page_actuelle = "🔮 Marchés Actifs"

if st.session_state.utilisateur_courant is None:
    st.markdown("<h1 style='text-align: center; font-size: 4rem; margin-top:50px;'>PRÉDICTIONS 🔮</h1>", unsafe_allow_html=True)
    with st.container():
        nom_choisi = st.selectbox("Utilisateur :", ["-- Choisir --"] + list(joueurs_autorises.keys()))
        mdp_saisi = st.text_input("Mot de passe :", type="password", placeholder="Saisir le mot de passe...")
        if st.button("Se connecter"):
            if nom_choisi != "-- Choisir --" and joueurs_autorises.get(nom_choisi) == mdp_saisi:
                st.session_state.utilisateur_courant = nom_choisi
                st.session_state.check_recompenses = True
                rafraichir()
            else:
                st.error("Identifiants incorrects.")
    st.stop()

# ==========================================
# 3. LE SYSTÈME À DOPAMINE DE RECONNEXION
# ==========================================
user = st.session_state.utilisateur_courant

if st.session_state.get("check_recompenses", False):
    historique_vu = db["utilisateurs"][user].get("historique_vu", [])
    marches_clos_non_vus = [q for q in db["questions"] if q["statut"] == "clos" and q["id"] not in historique_vu]
    
    if marches_clos_non_vus:
        q_en_cours = marches_clos_non_vus[0]
        pari_associe = next((p for p in db["paris"] if p["id_question"] == q_en_cours["id"] and p["joueur"] == user), None)
        
        st.markdown(f"<h2 style='text-align:center;'>🚨 RÉSULTAT REÇU ! 🚨</h2>", unsafe_allow_html=True)
        
        with st.container():
            balise_unique = f"dopamine-popup-{q_en_cours['id']}"
            html_recompense = f"<{balise_unique} style='display: block;'>"
            html_recompense += "<div class='reward-card'>"
            html_recompense += f"<h3 class='zoom-pop-text'>{q_en_cours['titre']}</h3>"
            html_recompense += f"<p class='zoom-pop-text delay-1' style='font-size: 1.2rem;'>La Vérité absolue : <b style='color:#39ff14;'>{q_en_cours['resultat']}</b></p>"
            
            if pari_associe:
                points_gagnes = pari_associe["credences"].get(q_en_cours["resultat"], 0)
                html_recompense += "<div class='zoom-pop-text delay-2'>"
                html_recompense += f"<p style='color:#ffff00; font-weight:bold;'>Ta crédence : {points_gagnes}%</p>"
                
                masque_restant = 100 - points_gagnes
                html_recompense += f"<style> @keyframes fluide-{q_en_cours['id']} {{ 0% {{ width: 100%; }} 100% {{ width: {masque_restant}%; }} }} </style>"
                html_recompense += f"<div class='xp-bar-container'><div class='xp-bar-overlay' style='animation: fluide-{q_en_cours['id']} 4.5s linear forwards;'><div class='sparks-front'></div></div></div>"
                
                html_recompense += "</div>"
                html_recompense += f"<h2 class='zoom-pop-text delay-3'>GAIN : +{points_gagnes} POINTS</h2>"
                
                if points_gagnes < 20: html_recompense += "<div class='zoom-pop-text delay-3'><div class='ball-broken'>🔮</div></div><h3 class='zoom-pop-text delay-3' style='color:#ff0055 !important; text-shadow:none;'>HONTES ET SANCTIONS.</h3><p class='zoom-pop-text delay-3'>Ton intuition a échoué.</p>"
                elif points_gagnes <= 50: html_recompense += "<div class='zoom-pop-text delay-3'><div class='ball-fade'>🔮</div></div><h3 class='zoom-pop-text delay-3' style='color:#ff00ff !important; text-shadow:none;'>C'est tiède... au moins tu as été humble.</h3><p class='zoom-pop-text delay-3'>Tu as limité la casse grâce à ton incertitude.</p>"
                elif points_gagnes <= 80: html_recompense += "<div class='zoom-pop-text delay-3'><div class='ball-glow'>🔮</div></div><h3 class='zoom-pop-text delay-3' style='color:#00ffff !important; text-shadow:none;'>Bien joué ! Tu as une bonne intuition !</h3><p class='zoom-pop-text delay-3'>La boule rayonne de puissance.</p>"
                else: html_recompense += "<div class='zoom-pop-text delay-3'><div class='third-eye-psy'>👁️⚙️⚡</div></div><h2 class='zoom-pop-text delay-3' style='color:#ffff00 !important; text-shadow: 0 0 20px #ff00ff;'>✨ DOPAMINE MAX !!! ✨</h2><h3 class='zoom-pop-text delay-3' style='color:#39ff14 !important;'>TROISIÈME ŒIL ÉVEILLÉ !</h3>"
            else:
                points_gagnes = 0
                html_recompense += "<div class='zoom-pop-text delay-2'><p>Tu n'avais pas enregistré de vision sur ce marché.</p><h2 style='color:#ff0055;'>GAIN : 0 POINTS</h2></div>"
                
            html_recompense += f"</div></{balise_unique}>" 
            
            st.markdown(html_recompense, unsafe_allow_html=True)
            
            if st.button("COLLECTER ET CONTINUER 🚀"):
                if "historique_vu" not in db["utilisateurs"][user]: db["utilisateurs"][user]["historique_vu"] = []
                db["utilisateurs"][user]["historique_vu"].append(q_en_cours["id"])
                save_data(db)
                if points_gagnes > 0: st.session_state.points_volants = points_gagnes
                rafraichir()
        st.stop()
    else:
        st.session_state.check_recompenses = False

# ==========================================
# 4. INTERFACE PRINCIPALE (SIDEBAR & GRAPHIQUE)
# ==========================================
score_user = db["utilisateurs"][user].get("score", 0)
mes_badges = "".join(db["utilisateurs"][user].get("badges", []))

# POINTS VOLANTS
if st.session_state.get("points_volants") is not None:
    pts = st.session_state.points_volants
    st.markdown(f"<div class='flying-points'>+{pts}</div>", unsafe_allow_html=True)
    jouer_son_invisible("validation.mp3") # <--- AJOUTE CETTE LIGNE ICI
    st.session_state.points_volants = None

with st.sidebar:
    avatar_b64 = db["utilisateurs"][user].get("avatar")
    html_avatar = f"<img src='data:image/png;base64,{avatar_b64}' class='avatar-pixel'>" if avatar_b64 else "👤 "
    
    # On affiche l'avatar, le nom et les badges ensemble
    st.markdown(f"<h3 style='margin-bottom:0;'>{html_avatar}{user} {mes_badges}</h3>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='color:#39ff14; text-shadow: none;'>Niveau : {obtenir_rang(score_user)}</h4>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='color:#39ff14; text-shadow: none;'>Niveau : {obtenir_rang(score_user)}</h4>", unsafe_allow_html=True)
    st.metric(label="Total des points", value=f"{round(score_user, 1)}")
    
    # PROGRESSION (LEVELLING)
    if score_user < 100: pourcentage = (score_user / 100) * 33.33
    elif score_user < 300: pourcentage = 33.33 + ((score_user - 100) / 200) * 33.33
    elif score_user < 600: pourcentage = 66.66 + ((score_user - 300) / 300) * 33.33
    else: pourcentage = 100
        
    html_prog = f"""
    <div class='progress-wrapper'>
        <div class='progress-track'>
            <div class='progress-fill' style='width: {pourcentage}%'></div>
            <div class='nodes-container'>
                <div class='node-wrapper {"active" if score_user >= 0 else ""}'>
                    <div class='node {"active" if score_user >= 0 else ""}'></div><span class='node-label'>Débutant</span>
                </div>
                <div class='node-wrapper {"active" if score_user >= 100 else ""}'>
                    <div class='node {"active" if score_user >= 100 else ""}'></div><span class='node-label'>Initié</span>
                </div>
                <div class='node-wrapper {"active" if score_user >= 300 else ""}'>
                    <div class='node {"active" if score_user >= 300 else ""}'></div><span class='node-label'>Expert</span>
                </div>
                <div class='node-wrapper {"active" if score_user >= 600 else ""}'>
                    <div class='node {"active" if score_user >= 600 else ""}'></div><span class='node-label'>Oracle</span>
                </div>
            </div>
        </div><div style='height: 30px;'></div> 
    </div>
    """
    st.markdown(html_prog, unsafe_allow_html=True)
    
    # DATA VIZ : LE GRAPHIQUE DES DERNIERS GAINS
    gains = db["utilisateurs"][user].get("gains_historique", [])
    if gains:
        st.markdown("<p style='color:#00ffff; font-weight:bold; font-size:0.9rem;'>📊 ÉVOLUTION DES GAINS</p>", unsafe_allow_html=True)
        chart_html = "<div style='display:flex; align-items:flex-end; height:50px; gap:4px; margin-bottom:15px; background:rgba(0,0,0,0.4); padding:5px; border-radius:5px; border-bottom:2px solid #333;'>"
        for g in gains[-12:]: # Affiche les 12 derniers paris
            color = "#39ff14" if g >= 50 else ("#ff0055" if g < 20 else "#ffff00")
            h = max(5, g) # Hauteur proportionnelle (min 5%)
            chart_html += f"<div style='flex:1; background:{color}; height:{h}%; border-radius:2px 2px 0 0; box-shadow:0 0 5px {color};' title='+{g} pts'></div>"
        chart_html += "</div>"
        st.markdown(chart_html, unsafe_allow_html=True)
    
    st.markdown("""<hr style="border-color: #ff00ff;">""", unsafe_allow_html=True)
    if user == "Noe": st.markdown("<span style='color:#ffff00; font-weight: bold;'>⚙️ Administration activée</span>", unsafe_allow_html=True)
    if st.button("Se déconnecter"):
        st.session_state.utilisateur_courant = None
        rafraichir()

# ==========================================
# 5. NAVIGATION & MARCHÉS ACTIFS
# ==========================================
liste_pages = ["🔮 Marchés Actifs", "🏆 Classement", "➕ Créer", "📖 Règles","👾 Profil"]
def changer_page(): st.session_state.page_actuelle = st.session_state.radio_menu

choix_menu = st.radio("Menu", liste_pages, horizontal=True, key="radio_menu", index=liste_pages.index(st.session_state.page_actuelle), on_change=changer_page, label_visibility="collapsed")

def cloturer_et_distribuer_badges(q_id, opt_gagnante):
    """Fonction Admin : Ferme le marché, distribue points, data viz et badges"""
    for q_db in db["questions"]:
        if q_db["id"] == q_id:
            q_db["statut"], q_db["resultat"] = "clos", opt_gagnante
    
    for p in [p for p in db["paris"] if p["id_question"] == q_id]:
        pts = p["credences"].get(opt_gagnante, 0)
        joueur = p["joueur"]
        db["utilisateurs"][joueur]["score"] += pts
        
        # 1. Data Viz : Sauvegarde dans l'historique
        db["utilisateurs"][joueur].setdefault("gains_historique", []).append(pts)
        
        # 2. Succès / Badges
        badges = db["utilisateurs"][joueur].setdefault("badges", [])
        # Sniper : 100% de réussite
        if pts == 100 and "🎯" not in badges: badges.append("🎯")
        # Kamikaze : 100% sur un choix perdant
        if pts == 0 and any(v == 100 for v in p["credences"].values()) and "💀" not in badges: badges.append("💀")
        # Renard : Au moins 5 paris terminés
        if len(db["utilisateurs"][joueur]["gains_historique"]) >= 5 and "🦊" not in badges: badges.append("🦊")
    save_data(db)

if st.session_state.page_actuelle == "🔮 Marchés Actifs":
    questions_en_cours = [q for q in db["questions"] if q["statut"] == "en cours"]
    if not questions_en_cours: st.info("Aucune question en cours. Va dans 'Créer'.")
        
    for q in reversed(questions_en_cours):
        paris_q = [p for p in db["paris"] if p["id_question"] == q["id"]]
        mon_pari = next((p for p in paris_q if p["joueur"] == user), None)
        
        # --- CAS 1 : LE JOUEUR N'A PAS ENCORE VOTÉ ---
        if mon_pari is None:
            with st.container():
                st.markdown(f"### {q['titre']}")
                try:
                    jours_restants = (datetime.strptime(q['deadline'], "%Y-%m-%d").date() - datetime.now().date()).days
                    st.caption(f"Créé par {q['auteur']} | Reste {jours_restants} jour(s)")
                except: pass

                # ADMIN Noe (OUVERT)
                if user == "Noe":
                    with st.expander("⚙️ Clôturer (Admin)"):
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            opt_gagnante = st.selectbox("Résultat réel :", ["-- Choisir --"] + q["options"], key=f"sel_ouv_{q['id']}")
                            if st.button("Valider le résultat", key=f"close_ouv_{q['id']}"):
                                if opt_gagnante != "-- Choisir --":
                                    cloturer_et_distribuer_badges(q["id"], opt_gagnante)
                                    trigger_animation("RÉSULTAT SCELLÉ 🔮")
                        with c2:
                            st.write(""); st.write("")
                            if st.button("Effacer", key=f"del_ouv_{q['id']}"):
                                db["questions"] = [x for x in db["questions"] if x["id"] != q["id"]]
                                db["paris"] = [p for p in db["paris"] if p["id_question"] != q["id"]]
                                save_data(db)
                                rafraichir()

                # VOTE
                st.markdown("<p style='color:#ffff00; font-weight:bold;'>Répartis tes probabilités (Total obligatoire : 100%)</p>", unsafe_allow_html=True)
                creds = {}
                for opt in q["options"]:
                    creds[opt] = st.slider(opt, 0, 100, 100 // len(q["options"]), key=f"sl_{q['id']}_{opt}")
                
                if sum(creds.values()) == 100:
                    if st.button("Valider ma prédiction", key=f"sub_{q['id']}"):
                        db["paris"].append({"id_question": q["id"], "joueur": user, "credences": creds})
                        save_data(db)
                        trigger_animation("PRÉDICTION ENREGISTRÉE", jouer_son=True)
                else: st.error(f"Erreur : Total actuel = {sum(creds.values())}%.")
                
                # SOCIAL : DÉBAT MATRICIEL
                st.markdown("<br><h4 style='color:#ff00ff; font-size:1.1rem;'>💬 Débat Matriciel</h4>", unsafe_allow_html=True)
                for c in q.get("commentaires", []):
                    st.markdown(f"<div class='chat-container'><span class='chat-user'>{c['joueur']} :</span><span class='chat-msg'>{c['texte']}</span></div>", unsafe_allow_html=True)
                
                new_com = st.text_input("Lâche ta vérité...", key=f"chat_ouv_{q['id']}")
                if st.button("Envoyer", key=f"send_ouv_{q['id']}"):
                    if new_com.strip():
                        if "commentaires" not in q: q["commentaires"] = []
                        q["commentaires"].append({"joueur": user, "texte": new_com.strip()})
                        for db_q in db["questions"]:
                            if db_q["id"] == q["id"]: db_q["commentaires"] = q["commentaires"]
                        save_data(db)
                        rafraichir()
        
        # --- CAS 2 : LE JOUEUR A DÉJÀ VOTÉ (ACCORDÉON) ---
        else:
            with st.expander(f"🔮 {q['titre']} (Validé)"):
                try:
                    jours_restants = (datetime.strptime(q['deadline'], "%Y-%m-%d").date() - datetime.now().date()).days
                    st.caption(f"Créé par {q['auteur']} | Reste {jours_restants} jour(s)")
                except: pass

                # ADMIN Noe (CLOS)
                if user == "Noe":
                    st.markdown("<span style='color:#ffff00; font-weight:bold;'>⚙️ Administration :</span>", unsafe_allow_html=True)
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        opt_gagnante = st.selectbox("Résultat réel :", ["-- Choisir --"] + q["options"], key=f"sel_clos_{q['id']}")
                        if st.button("Valider le résultat", key=f"close_clos_{q['id']}"):
                            if opt_gagnante != "-- Choisir --":
                                cloturer_et_distribuer_badges(q["id"], opt_gagnante)
                                trigger_animation("RÉSULTAT SCELLÉ 🔮",jouer_son=True)
                    with c2:
                        st.write(""); st.write("")
                        if st.button("Effacer", key=f"del_clos_{q['id']}"):
                            db["questions"] = [x for x in db["questions"] if x["id"] != q["id"]]
                            db["paris"] = [p for p in db["paris"] if p["id_question"] != q["id"]]
                            save_data(db)
                            rafraichir()
                    st.write("---")

                cols = st.columns(len(q['options']))
                for idx, opt in enumerate(q["options"]):
                    m_cred = sum(p["credences"].get(opt, 0) for p in paris_q) / len(paris_q) if paris_q else 0
                    cote = round(100 / m_cred, 2) if m_cred > 0 else "Max"
                    with cols[idx]:
                        st.markdown(f"<div style='color:#ffff00; font-size:1.3rem; font-weight:bold;'>{opt} : {mon_pari['credences'].get(opt, 0)}%</div>", unsafe_allow_html=True)
                        st.caption(f"Cote actuelle : x{cote}")
                        
                # SOCIAL : DÉBAT MATRICIEL
                st.markdown("<br><h4 style='color:#ff00ff; font-size:1.1rem;'>💬 Débat Matriciel</h4>", unsafe_allow_html=True)
                for c in q.get("commentaires", []):
                    st.markdown(f"<div class='chat-container'><span class='chat-user'>{c['joueur']} :</span><span class='chat-msg'>{c['texte']}</span></div>", unsafe_allow_html=True)
                
                new_com = st.text_input("Lâche ta vérité...", key=f"chat_clos_{q['id']}")
                if st.button("Envoyer", key=f"send_clos_{q['id']}"):
                    if new_com.strip():
                        if "commentaires" not in q: q["commentaires"] = []
                        q["commentaires"].append({"joueur": user, "texte": new_com.strip()})
                        for db_q in db["questions"]:
                            if db_q["id"] == q["id"]: db_q["commentaires"] = q["commentaires"]
                        save_data(db)
                        rafraichir()

# ==========================================
# 6. AUTRES ONGLETS
# ==========================================
elif st.session_state.page_actuelle == "🏆 Classement":
    st.subheader("LEADERBOARD GLOBAL")
    # AFFICHE LES BADGES DANS LE CLASSEMENT !
    scores_data = []
    for k, v in db["utilisateurs"].items():
        av_b64 = v.get("avatar")
        img_html = f"<img src='data:image/png;base64,{av_b64}' class='avatar-pixel' style='width:30px; height:30px;'>" if av_b64 else "👤"
        joueur_complet = f"{img_html} {k} {''.join(v.get('badges', []))}"
        scores_data.append({"Joueur": joueur_complet, "Niveau": obtenir_rang(v["score"]), "Points": round(v["score"], 1)})    
        df_scores = pd.DataFrame(scores_data).sort_values(by="Points", ascending=False)
    
    html_table = "<table class='hyper-table'><thead><tr><th>Joueur</th><th>Niveau</th><th>Points</th></tr></thead><tbody>"
    for _, row in df_scores.iterrows():
        html_table += f"<tr><td>{row['Joueur']}</td><td>{row['Niveau']}</td><td>{row['Points']}</td></tr>"
    html_table += "</tbody></table>"
    st.markdown(html_table, unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("HISTORIQUE DES RÉSULTATS")
    closes = [q for q in db["questions"] if q["statut"] == "clos"]
    for q in reversed(closes):
        mon_p = next((p for p in db["paris"] if p["id_question"] == q["id"] and p["joueur"] == user), None)
        with st.expander(f"🔮 {q['titre']}"):
            st.markdown(f"**La réponse était :** <span style='color:#39ff14; font-weight:bold;'>{q['resultat']}</span>", unsafe_allow_html=True)
            if mon_p:
                pts = mon_p["credences"].get(q['resultat'], 0)
                st.markdown(f"Tu avais parié : {pts}% | Points gagnés : +{pts}", unsafe_allow_html=True)

elif st.session_state.page_actuelle == "➕ Créer":
    st.subheader("POSER UNE QUESTION")
    titre = st.text_input("La question :", placeholder="Exemple : Thomas aura-t-il son permis avant juin ?")
    opts = st.text_area("Les réponses possibles (Une par ligne) :", "Oui\nNon")
    dead = st.date_input("Date limite de l'événement :")
    
    if st.button("Publier la question"):
        opts_list = [o.strip() for o in opts.split('\n') if o.strip()]
        if titre and len(opts_list) >= 2:
            db["questions"].append({"id": int(time.time()), "titre": titre, "auteur": user, "options": opts_list, "deadline": str(dead), "statut": "en cours", "resultat": None, "commentaires": []})
            save_data(db)
            st.session_state.page_actuelle = "🔮 Marchés Actifs"
            trigger_animation("QUESTION PUBLIÉE 🔮")
        else: st.error("Erreur de paramètres.")

elif st.session_state.page_actuelle == "📖 Règles":
    st.subheader("WIKI : LE SYSTÈME DE PRÉDICTION")
    
    html_regles = "<div style='background: rgba(0,0,0,0.8); padding: 25px; border: 3px solid #ff00ff; border-radius: 10px;'>"
    html_regles += "<h4 style='color: #00ffff;'>1. L'ESPRIT DU JEU : LA CALIBRATION</h4>"
    html_regles += "<p>Ici, nous ne jouons pas au Loto. Un bon prévisionniste est un <b>Renard</b> : il nuance son avis. Ton objectif est d'être le plus proche possible de la réalité en allouant tes probabilités.</p><br>"
    
    html_regles += "<h4 style='color: #ff00ff;'>2. LA MÉCANIQUE : COMMENT ALLOUER</h4>"
    html_regles += "<ul><li><b>Jauges de crédence :</b> Tu disposes de 100 points de confiance à répartir entre les issues possibles.</li>"
    html_regles += "<li><b>Le total obligatoire :</b> La somme de tes jauges doit faire exactement 100%. Plus tu mets de points sur une option, plus tu prends de risques !</li></ul><br>"
    
    html_regles += "<h4 style='color: #39ff14;'>3. LE SYSTÈME DE SCORE ET SUCCÈS</h4>"
    html_regles += "<p style='padding: 10px; background: rgba(255,255,255,0.05); border-left: 4px solid #ffff00;'>Si l'option <b>A</b> est vraie, tu gagnes <b style='color:#ffff00;'>X points</b>, où <b>X</b> est le pourcentage que tu avais mis sur cette option.</p>"
    html_regles += "<p>Le jeu récompense aussi tes actions avec des <b>BADGES</b> :</p>"
    html_regles += "<ul style='list-style-type: none;'>"
    html_regles += "<li>🎯 <b>Sniper</b> : Trouve un résultat avec 100% de certitude.</li>"
    html_regles += "<li>💀 <b>Kamikaze</b> : Mets 100% sur un résultat qui s'avère faux.</li>"
    html_regles += "<li>🦊 <b>Renard</b> : Complète 5 marchés avec succès.</li></ul><br>"
    
    html_regles += "<h4 style='color: #ffd700;'>4. L'ASCENSION VERS L'ORACLE</h4>"
    html_regles += "<ul style='list-style-type: none;'>"
    html_regles += "<li>🌙 <b style='color:#00ffff;'>0 - 99 pts</b> : Débutant</li>"
    html_regles += "<li>🔮 <b style='color:#00ffff;'>100 - 299 pts</b> : Initié</li>"
    html_regles += "<li>⚡ <b style='color:#00ffff;'>300 - 599 pts</b> : Expert</li>"
    html_regles += "<li>🌐 <b style='color:#00ffff;'>600+ pts</b> : Oracle</li>"
    html_regles += "</ul></div>"
    
    st.markdown(html_regles, unsafe_allow_html=True)

elif st.session_state.page_actuelle == "👾 Profil":
    st.subheader("CRÉATEUR D'AVATAR")
    st.markdown("<p style='color:#00ffff;'>Dessine ton identité visuelle dans la matrice. Utilise les couleurs néons.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        stroke_color = st.color_picker("Couleur du pinceau :", "#39ff14")
        stroke_width = st.slider("Taille du pinceau :", 5, 25, 10, key="slider_pinceau")
        
        st.markdown("<br><p style='color:#ff00ff; font-weight:bold;'>Options :</p>", unsafe_allow_html=True)
        drawing_mode = st.radio("Outil :", ("freedraw", "line", "rect", "circle", "transform"), key="radio_outil")
    
    with col2:
        # Le Canvas avec un fond sombre cohérent avec le CSS
        canvas_result = st_canvas(
            fill_color="rgba(0, 0, 0, 0)", 
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_color="#050010",
            width=256,
            height=256,
            drawing_mode=drawing_mode,
            key="canvas_matrice"
        )
        
        if st.button("Sauvegarder l'Avatar 💾", key="btn_save_avatar"):
            if canvas_result.image_data is not None:
                # Récupération de l'image (numpy array)
                img_array = canvas_result.image_data.astype('uint8')
                img = Image.fromarray(img_array, 'RGBA')
                
                # Réduction en 32x32 pour un vrai look "Pixel Art"
                img = img.resize((32, 32), Image.Resampling.NEAREST)
                
                # Conversion en Base64
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # Sauvegarde BDD
                db["utilisateurs"][user]["avatar"] = img_str
                save_data(db)
                
                trigger_animation("AVATAR UPLOADÉ 👾", jouer_son=True)
