import streamlit as st
import json
import os
import random
from datetime import datetime
import time
import pandas as pd
import base64
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
import numpy as np
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import re # Pour nettoyer le texte renvoyé par l'IA

# ==========================================
# 0. CONFIGURATION & THÈME CSS (HYPERPOP + MATRIX)
# ==========================================
st.set_page_config(page_title="Prédictions", page_icon="🔮", layout="centered", initial_sidebar_state="expanded")


def activer_curseur_symbiote(svg_code):
    """Version stable 64x64 avec éradication du fond noir (Transparence)."""
    if not svg_code:
        return

    import base64
    import re
    import streamlit as st

    # 1. Nettoyage de base
    svg_curseur = re.sub(r'', '', svg_code, flags=re.DOTALL)
    svg_curseur = svg_curseur.replace("\n", " ").replace("```xml", "").replace("```", "").strip()

    # 2. Assurance-vie (Vérification de la balise)
    if not svg_curseur.lower().startswith("<svg"):
        svg_curseur = f'<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">{svg_curseur}</svg>'

    # 3. LE LASER ANTI-FOND (Rend le monstre transparent)
    # L'IA génère souvent un rectangle de 200x200 ou 100% en fond. On le détruit.
    # On vérifie les deux sens (width d'abord, ou height d'abord) pour être sûr de l'avoir !
    svg_curseur = re.sub(r'<rect[^>]*width=["\'](?:200|100%)["\'][^>]*height=["\'](?:200|100%)["\'][^>]*?/?>', '', svg_curseur, flags=re.IGNORECASE)
    svg_curseur = re.sub(r'<rect[^>]*height=["\'](?:200|100%)["\'][^>]*width=["\'](?:200|100%)["\'][^>]*?/?>', '', svg_curseur, flags=re.IGNORECASE)

    # 4. Mutation de Taille (64x64 - Gros mais 100% sécurisé)
    svg_curseur = re.sub(r'width="[^"]*"', 'width="64"', svg_curseur, count=1, flags=re.IGNORECASE)
    svg_curseur = re.sub(r'height="[^"]*"', 'height="64"', svg_curseur, count=1, flags=re.IGNORECASE)

    # 5. Encodage et Injection
    try:
        b64_svg = base64.b64encode(svg_curseur.encode('utf-8')).decode('utf-8')
        
        # Le '32 32' place la zone de clic parfaitement au centre du monstre de 64 pixels
        css_curseur = f"""
        <style>
            html, body, [class*="st-"] {{
                cursor: url('data:image/svg+xml;base64,{b64_svg}') 32 32, auto !important;
            }}
            button, a, input, [role="button"] {{
                cursor: url('data:image/svg+xml;base64,{b64_svg}') 32 32, pointer !important;
            }}
        </style>
        """
        st.markdown(css_curseur, unsafe_allow_html=True)
    except Exception as e:
        pass

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

        /* CSS DU CHAT (DÉBAT ) */
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

/* ==========================================
        /* L'AUTEL DES SEIGNEURS (LÉVITATION 3D HOLOGRAPHIQUE)
        /* ========================================== */
        .pantheon-container {
            display: flex;
            justify-content: center;
            align-items: flex-end;
            gap: 20px;
            margin: 40px 0 50px 0;
            width: 100%;
            /* C'est ici que la magie opère : on crée la boîte 3D */
            perspective: 1200px; 
            transform-style: preserve-3d;
        }

        .pantheon-card {
            background: rgba(5, 0, 16, 0.85) !important;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            font-family: 'Arial Black', sans-serif !important;
            transition: all 0.6s cubic-bezier(0.23, 1, 0.32, 1);
            position: relative;
            overflow: hidden;
            /* La carte doit conserver les effets 3D pour ses enfants (l'avatar) */
            transform-style: preserve-3d; 
            /* Flottaison anti-gravité perpétuelle */
            animation: float-holo 6s ease-in-out infinite alternate;
        }

        /* Désynchronisation de la gravité pour chaque carte */
        .card-2nd { animation-delay: 0s; }
        .card-1st { animation-delay: -2s; z-index: 10; }
        .card-3rd { animation-delay: -4s; }

        @keyframes float-holo {
            0% { transform: translateY(0px) rotateX(2deg) rotateY(0deg); }
            100% { transform: translateY(-12px) rotateX(-2deg) rotateY(3deg); }
        }

        /* L'EFFET DE DISTORSION AU SURVOL (LA LÉVITATION) */
        .pantheon-card:hover {
            animation: none; /* Stoppe la flottaison de base pour figer l'interaction */
            /* La carte s'écrase en arrière et tourne sur le côté */
            transform: translateY(-20px) scale(1.05) rotateX(20deg) rotateY(-15deg);
            z-index: 20;
        }

        /* LE FAISCEAU LASER HOLOGRAPHIQUE (Glass effect) */
        .pantheon-card::before {
            content: '';
            position: absolute;
            top: 0; left: -150%;
            width: 50%; height: 100%;
            background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.4) 50%, rgba(255,255,255,0) 100%);
            transform: skewX(-25deg);
            animation: shine-holo 7s infinite;
            pointer-events: none; /* Pour ne pas bloquer les clics */
            z-index: 5;
        }

        @keyframes shine-holo {
            0% { left: -150%; }
            15% { left: 200%; }
            100% { left: 200%; }
        }

        /* Amplification Thermonucléaire des Néons au survol */
        .card-1st:hover { box-shadow: -20px 20px 50px rgba(255, 255, 0, 0.5), inset 0 0 30px rgba(255, 255, 0, 0.4) !important; border-color: #ffffff !important; }
        .card-2nd:hover { box-shadow: -15px 15px 40px rgba(0, 255, 255, 0.5), inset 0 0 25px rgba(0, 255, 255, 0.4) !important; border-color: #ffffff !important; }
        .card-3rd:hover { box-shadow: -15px 15px 40px rgba(255, 0, 255, 0.5), inset 0 0 25px rgba(255, 0, 255, 0.4) !important; border-color: #ffffff !important; }

        /* PARAMÉTRAGE DES AVATARS */
        .pantheon-avatar {
            width: 80px;
            height: 80px;
            border-radius: 6px;
            image-rendering: pixelated;
            margin: 10px auto;
            display: block;
            transition: all 0.6s cubic-bezier(0.23, 1, 0.32, 1);
            transform: translateZ(0px); /* Point de départ plat */
            position: relative;
            z-index: 10;
        }

        /* LE DÉTACHEMENT 3D AU SURVOL : L'avatar sort littéralement de l'écran */
        .pantheon-card:hover .pantheon-avatar {
            transform: translateZ(60px) scale(1.2);
            box-shadow: 10px 20px 30px rgba(0,0,0,0.9), 0 0 20px currentColor;
        }

        /* DÉTAILS DE BASE DES CARTES */
        .card-1st { border: 4px solid #ffff00 !important; box-shadow: 0 0 30px #ffff00, inset 0 0 15px rgba(255, 255, 0, 0.2) !important; width: 220px; height: 250px; }
        .card-1st .pantheon-avatar { width: 100px; height: 100px; box-shadow: 0 0 20px #ffff00; border: 2px solid #ffff00; }
        .card-2nd { border: 3px solid #00ffff !important; box-shadow: 0 0 20px #00ffff, inset 0 0 10px rgba(0, 255, 255, 0.1) !important; width: 180px; height: 205px; }
        .card-3rd { border: 3px solid #ff00ff !important; box-shadow: 0 0 20px #ff00ff, inset 0 0 10px rgba(255, 0, 255, 0.1) !important; width: 180px; height: 190px; }

        .pantheon-rank { font-size: 0.9rem; letter-spacing: 2px; text-transform: uppercase; font-weight: 900; }
        .pantheon-name { color: #ffffff !important; font-size: 1.2rem; margin: 8px 0 4px 0; text-shadow: 0 0 5px rgba(255,255,255,0.6); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; transform: translateZ(30px); transition: all 0.6s; }
        .pantheon-card:hover .pantheon-name { transform: translateZ(40px); }
        .pantheon-pts { color: #39ff14 !important; font-size: 1.1rem; font-weight: 900; text-shadow: 0 0 5px rgba(57, 255, 20, 0.3); transform: translateZ(20px); transition: all 0.6s; }
        .pantheon-card:hover .pantheon-pts { transform: translateZ(30px); }

        .pantheon-empty-av { width: 80px; height: 80px; background: #12002f; border: 2px dashed #333; border-radius: 6px; margin: 10px auto; display: flex; align-items: center; justify-content: center; font-size: 2rem; transition: all 0.6s; transform: translateZ(0px); }
        .pantheon-card:hover .pantheon-empty-av { transform: translateZ(60px) scale(1.2); box-shadow: 10px 20px 30px rgba(0,0,0,0.9); }
        .card-1st .pantheon-empty-av { width: 100px; height: 100px; font-size: 2.5rem; }
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



def muter_entite_avec_gemini(forme_actuelle, requete, niveau, style, dernier_theme):
    """
    Fait appel à Gemini pour générer le Familier ET ses 3 attaques (Pierre, Feuille, Ciseaux).
    Retourne une chaîne JSON structurée.
    """
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"""Tu es un Architecte. Ta mission est de générer un familier virtuel ET ses 3 attaques uniques basées sur le principe du Pierre-Feuille-Ciseaux.
        - État actuel : {forme_actuelle}
        - Demande de mutation du joueur : {requete}
        - Alignement : {style}
        - Thème récent : {dernier_theme}

        Règle du SVG de base : sois créatif, anime des yeux expressifs et anime les membres
        
        RÈGLES DU PIERRE-FEUILLE-CISEAUX :
        1. PIERRE : Représente la Défense, la Terre, le Bouclier, ou un projectile lourd.
        2. FEUILLE : Représente un souffle d'énergie, la mitraille, le Vent, 
        3. CISEAUX : Représente la Vitesse, le Tranchant, les Lames, les Griffes ou un tir sniper

        CONTRAINTES SVG :
        - Tous les SVGs doivent faire exactement viewBox="0 0 200 200" width="100%" height="100%".
        - NE METS AUCUN FOND (pas de rect de fond, transparence totale).
        - Les overlays d'attaque (pierre, feuille, ciseaux) ne doivent contenir QUE l'effet visuel de l'attaque, ils seront superposés sur le familier.
        - Utilise des animations SMIL (<animate>) dans les overlays pour donner de l'impact (ex: des griffes qui apparaissent, un bouclier qui pulse, des tirs).
        - les animations doivent être cohérentes avec la nature du perso
        
        RÉPONSE ATTENDUE : UNIQUEMENT UN OBJET JSON STRICT. AUCUN TEXTE AVANT NI APRÈS.
        Format JSON requis :
        {{
            "svg_base": "<svg ...> ... le corps du familier ... </svg>",
            "attaques": {{
                "pierre": {{
                    "nom": "Nom stylé de l'attaque défensive",
                    "svg_overlay": "<svg ...> ... effet bouclier/lourd ... </svg>"
                }},
                "feuille": {{
                    "nom": "Nom stylé de l'attaque de zone",
                    "svg_overlay": "<svg ...> ... effet onde/énergie ... </svg>"
                }},
                "ciseaux": {{
                    "nom": "Nom stylé de l'attaque tranchante",
                    "svg_overlay": "<svg ...> ... effet griffes/lames ... </svg>"
                }}
            }}
        }}
        """
        
        reponse = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        # Nettoyage pour s'assurer qu'on a bien que le JSON
        texte_brut = reponse.text.strip()
        texte_brut = texte_brut.replace("```json", "").replace("```", "").strip()
        
        return texte_brut
        
    except Exception as e:
        return f'{{"erreur": "{str(e)}"}}'

def forger_attaque_gemini(desc_familier, slot_attaque, nom_attaque, desc_attaque):
    # Version blindée : AUCUN triple guillemet pour ne pas faire planter GitHub
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = (
            "Tu es un Forgeron Cyberpunk. Ta mission est de générer UNE SEULE animation d'attaque au format SVG pour un familier.\n"
            f"- Apparence du familier lançant l'attaque : {desc_familier}\n"
            f"- Emplacement de l'attaque : {slot_attaque}\n"
            f"- Nom choisi par le joueur : {nom_attaque}\n"
            f"- Description et Type voulu : {desc_attaque}\n\n"
            "DIRECTIVES D'ANIMATION SVG (CRUCIAL) :\n"
            "- Le SVG doit faire viewBox='0 0 200 200' width='100%' height='100%'. Transparent (aucun rect de fond).\n"
            "- Ne dessine PAS le familier. Dessine UNIQUEMENT l'effet visuel de l'attaque (il sera superposé).\n\n"
            "RÈGLES SELON LE TYPE D'ATTAQUE :\n"
            "1. BOUCLIER / AURA (Sur place) : Anime au centre (autour de cx=100, cy=100). Ex: dôme qui pulse.\n"
            "2. PROJECTILE / TIR : Le tir DOIT partir du centre (x=100) et aller vers la DROITE de l'écran (x=300). L'arène inversera automatiquement le tir pour l'adversaire.\n"
            "3. SLASH / MÊLÉE : Dessine des arcs de cercle ou lignes obliques qui apparaissent et disparaissent très vite au centre.\n\n"
            "RÉPONSE ATTENDUE : UNIQUEMENT UN OBJET JSON STRICT. AUCUN TEXTE AVANT NI APRÈS.\n"
            "Format JSON requis :\n"
            "{\n"
            f"    \"nom\": \"{nom_attaque}\",\n"
            "    \"svg_overlay\": \"<svg> ... l'animation ... </svg>\"\n"
            "}"
        )
        
        reponse = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        texte_brut = reponse.text.strip().replace("```json", "").replace("```", "").strip()
        return texte_brut
        
    except Exception as e:
        # Formatage sécurisé sans f-string complexe
        return '{"erreur": "' + str(e).replace('"', "'") + '"}'

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
    
    # MAJ Structure Utilisateurs (avec support Avatar et Brins ADN)
    for nom in joueurs_autorises.keys():
        if nom not in db["utilisateurs"]:
            # ---> NOUVEAU JOUEUR : 50 BRINS D'ADN AU DÉMARRAGE <---
            db["utilisateurs"][nom] = {
                "score": 0, 
                "brins_adn": 50, 
                "classe_familier": "Équilibré", 
                "historique_vu": [], 
                "badges": [], 
                "gains_historique": [], 
                "avatar": None
            }
            modifie = True
        else:
            # ---> MISE À JOUR (Si le champ manquait, on donne 50 aussi) <---
            if "classe_familier" not in db["utilisateurs"][nom]: db["utilisateurs"][nom]["classe_familier"] = "Équilibré"; modifie = True
            if "brins_adn" not in db["utilisateurs"][nom]: db["utilisateurs"][nom]["brins_adn"] = 50; modifie = True
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

def calculer_bilan_pari(base_win, classe):
    """
    Calcule le gain, la perte et le net en fonction de la classe du familier.
    base_win : les points mis sur la bonne réponse (ex: 80)
    base_loss : les points mis sur les mauvaises réponses (ex: 20)
    """
    base_loss = 100 - base_win
    
    if "Kamikaze" in classe:
        gain = base_win * 1.15  # +15% de bonus de gain
        perte = base_loss * 1.10 # 10% de malus (on perd plus)
    elif "Prudent" in classe:
        gain = base_win * 1.00   # Gain normal
        perte = base_loss * 0.85 # Bouclier : on réduit la perte de 15%
    else: # Équilibré (ou joueur sans familier)
        gain = base_win
        perte = base_loss
        
    net = round(gain - perte, 1)
    return gain, perte, net

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
# VIRUS SYMBIOTIQUE : ACTIVATION DU CURSEUR
# ==========================================
# On récupère le nom de l'utilisateur connecté grâce à ta variable de session
user = st.session_state.utilisateur_courant

# On vérifie si l'utilisateur est bien dans la base de données
if user in db.get("utilisateurs", {}):
    # On cherche son familier
    familier_du_joueur = db["utilisateurs"][user].get("familier_svg", None)
    
    # S'il en a un, on lance la mutation du curseur !
    if familier_du_joueur:
        activer_curseur_symbiote(familier_du_joueur)

# ==========================================
# 3. LE SYSTÈME À DOPAMINE DE RECONNEXION
# ==========================================
user = st.session_state.utilisateur_courant

if st.session_state.get("check_recompenses", False):
    if "historique_vu" not in db["utilisateurs"][user]: 
        db["utilisateurs"][user]["historique_vu"] = []
        
    historique_vu = db["utilisateurs"][user]["historique_vu"]
    marches_clos_non_vus = [q for q in db["questions"] if q["statut"] == "clos" and q["id"] not in historique_vu]
    
    marches_a_afficher = []
    modifications_silencieuses = False
    
    for q in marches_clos_non_vus:
        pari = next((p for p in db["paris"] if p["id_question"] == q["id"] and p["joueur"] == user), None)
        if pari:
            marches_a_afficher.append((q, pari))
        else:
            db["utilisateurs"][user]["historique_vu"].append(q["id"])
            modifications_silencieuses = True
            
    if modifications_silencieuses:
        save_data(db) 
    
    if marches_a_afficher:
        q_en_cours, pari_associe = marches_a_afficher[0]
        
        # ---------------------------------------------------------
        # NOUVEAU : SI C'EST UN COMBAT, ON JOUE LE REPLAY AVANT !
        # ---------------------------------------------------------
        if q_en_cours.get("type") == "combat" and not st.session_state.get(f"replay_{q_en_cours['id']}"):
            st.markdown(f"<h2 style='text-align:center; color:#ff00ff; text-shadow:0 0 15px #ff00ff;'>⚔️ REPLAY DU COMBAT : {q_en_cours['titre']} ⚔️</h2>", unsafe_allow_html=True)
            
            import streamlit.components.v1 as components
            import json
            
            # Injection sécurisée de l'animation stockée
            html_arena = q_en_cours.get("html_combat", "<div style='color:white;'>Erreur de chargement de l'arène.</div>")
            components.html(html_arena, height=450)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("VOIR LES RÉSULTATS DU PARI 🚀", use_container_width=True):
                st.session_state[f"replay_{q_en_cours['id']}"] = True
                st.rerun()
            st.stop()
        # ---------------------------------------------------------
        
        # LA SUITE CLASSIQUE (Popup de gains)
        st.markdown(f"<h2 style='text-align:center;'>🚨 RÉSULTAT REÇU ! 🚨</h2>", unsafe_allow_html=True)
        
        with st.container():
            balise_unique = f"dopamine-popup-{q_en_cours['id']}"
            html_recompense = f"<{balise_unique} style='display: block;'>"
            html_recompense += "<div class='reward-card'>"
            html_recompense += f"<h3 class='zoom-pop-text'>{q_en_cours['titre']}</h3>"
            html_recompense += f"<p class='zoom-pop-text delay-1' style='font-size: 1.2rem;'>La Vérité absolue : <b style='color:#39ff14;'>{q_en_cours['resultat']}</b></p>"
            
            classe = db["utilisateurs"][user].get("classe_familier", "Équilibré")
            base_win = pari_associe["credences"].get(q_en_cours["resultat"], 0)
            
            gain, perte, net_pts = calculer_bilan_pari(base_win, classe)
            
            html_recompense += "<div class='zoom-pop-text delay-2'>"
            html_recompense += f"<p style='color:#ffff00; font-weight:bold;'>Ta crédence : {base_win}%</p>"
            html_recompense += f"<p style='color:#00ffff; font-size: 0.9rem;'>Alignement Actif : {classe}</p>"
            
            masque_restant = 100 - base_win
            html_recompense += f"<style> @keyframes fluide-{q_en_cours['id']} {{ 0% {{ width: 100%; }} 100% {{ width: {masque_restant}%; }} }} </style>"
            html_recompense += f"<div class='xp-bar-container'><div class='xp-bar-overlay' style='animation: fluide-{q_en_cours['id']} 4.5s linear forwards;'><div class='sparks-front'></div></div></div>"
            html_recompense += "</div>"
            
            if net_pts > 0:
                html_recompense += f"<h2 class='zoom-pop-text delay-3'>BILAN NET : +{net_pts} PTS</h2>"
            else:
                html_recompense += f"<h2 class='zoom-pop-text delay-3' style='color:#ff0055;'>BILAN NET : {net_pts} PTS</h2>"
            
            if net_pts < 0: 
                html_recompense += "<div class='zoom-pop-text delay-3'><div class='ball-broken'>🔮</div></div><h3 class='zoom-pop-text delay-3' style='color:#ff0055 !important; text-shadow:none;'>SANCTION .</h3><p class='zoom-pop-text delay-3'>Ton score vient d'être saigné.</p>"
            elif net_pts == 0: 
                html_recompense += "<div class='zoom-pop-text delay-3'><div class='ball-fade'>🔮</div></div><h3 class='zoom-pop-text delay-3' style='color:#aaaaaa !important; text-shadow:none;'>Pari Blanc.</h3><p class='zoom-pop-text delay-3'>Tu n'as rien gagné, rien perdu.</p>"
            elif net_pts <= 40: 
                html_recompense += "<div class='zoom-pop-text delay-3'><div class='ball-glow'>🔮</div></div><h3 class='zoom-pop-text delay-3' style='color:#00ffff !important; text-shadow:none;'>Bénéfice Mineur.</h3><p class='zoom-pop-text delay-3'>Ton intuition te rapporte quelques points.</p>"
            else: 
                html_recompense += "<div class='zoom-pop-text delay-3'><div class='third-eye-psy'>👁️⚙️⚡</div></div><h2 class='zoom-pop-text delay-3' style='color:#ffff00 !important; text-shadow: 0 0 20px #ff00ff;'>✨ DOPAMINE MAX !!! ✨</h2><h3 class='zoom-pop-text delay-3' style='color:#39ff14 !important;'>ASCENSION VALIDÉE !</h3>"
            
            points_gagnes_animation = net_pts 
            html_recompense += f"</div></{balise_unique}>" 
            
            st.markdown(html_recompense, unsafe_allow_html=True)
            
            if st.button("COLLECTER ET CONTINUER 🚀"):
                db["utilisateurs"][user]["historique_vu"].append(q_en_cours["id"])
                save_data(db)
                if points_gagnes_animation > 0: 
                    st.session_state.points_volants = points_gagnes_animation
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
    st.metric(label="Total des points", value=f"{round(score_user, 1)}")
    # --- NOUVEAU : AFFICHAGE DU PORTEFEUILLE ---
    brins_user = db["utilisateurs"][user].get("brins_adn", 0)
    st.metric(label="🧬 Brins d'ADN", value=f"{round(brins_user, 1)}")
    # -------------------------------------------
    
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
liste_pages = ["🔮 Marchés Actifs", "🏆 Classement", "➕ Créer", "📖 Règles","👾 Profil","🧬 Clinique Cybernétique","⚔️ Arène"]
def changer_page(): st.session_state.page_actuelle = st.session_state.radio_menu

choix_menu = st.radio("Menu", liste_pages, horizontal=True, key="radio_menu", index=liste_pages.index(st.session_state.page_actuelle), on_change=changer_page, label_visibility="collapsed")

def cloturer_et_distribuer_badges(q_id, opt_gagnante):
    """Fonction Admin : Ferme le marché, distribue points, data viz et badges"""
    for q_db in db["questions"]:
        if q_db["id"] == q_id:
            q_db["statut"], q_db["resultat"] = "clos", opt_gagnante
    
    for p in [p for p in db["paris"] if p["id_question"] == q_id]:
        joueur = p["joueur"]
        classe = db["utilisateurs"][joueur].get("classe_familier", "Équilibré")
        base_win = p["credences"].get(opt_gagnante, 0)
        
        # 1. On appelle le nouveau moteur mathématique
        _, _, net_pts = calculer_bilan_pari(base_win, classe)
        
        # 2. On applique les conséquences (Score et Brins d'ADN)
        db["utilisateurs"][joueur]["score"] += net_pts
        nouveau_brins = db["utilisateurs"][joueur].get("brins_adn", 0) + net_pts
        db["utilisateurs"][joueur]["brins_adn"] = max(0, nouveau_brins) # Les brins ne tombent pas sous zéro
        
        # 3. Data Viz : Sauvegarde dans l'historique (on sauvegarde le gain net)
        db["utilisateurs"][joueur].setdefault("gains_historique", []).append(net_pts)
        
        # 4. Succès / Badges
        badges = db["utilisateurs"][joueur].setdefault("badges", [])
        if base_win == 100 and "🎯" not in badges: badges.append("🎯")
        if base_win == 0 and any(v == 100 for v in p["credences"].values()) and "💀" not in badges: badges.append("💀")
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
                
                # SOCIAL : DÉBAT 
                st.markdown("<br><h4 style='color:#ff00ff; font-size:1.1rem;'>💬 Débat </h4>", unsafe_allow_html=True)
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
                        
                # SOCIAL : DÉBAT 
                st.markdown("<br><h4 style='color:#ff00ff; font-size:1.1rem;'>💬 Débat </h4>", unsafe_allow_html=True)
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
    import re
    import json
    import random
    import streamlit.components.v1 as components
    
    st.subheader("LE BESTIAIRE ")

    st.markdown("<p style='color:#ff0055; font-weight:bold; font-size:1.2rem; text-align:center;'>🚨 INTRUSION DÉTECTÉE : Cliquez n'importe où sur l'écran, bougez la souris pour esquiver et visez avec le tir automatique ! (Max 3 cibles) 🚨</p>", unsafe_allow_html=True)

    # ==========================================
    # 🌟 MINIJEU CACHÉ : SURVIE  
    # ==========================================
    st.markdown("<div id='cyber-game-anchor'></div>", unsafe_allow_html=True)
    
    def nettoyer_svg_game(svg_code):
        if not svg_code: return ""
        svg_code = re.sub(r'', '', svg_code, flags=re.DOTALL)
        svg_code = svg_code.replace("```xml", "").replace("```html", "").replace("```", "")
        svg_code = re.sub(r'<rect[^>]*width=["\'](?:200|100%)["\'][^>]*height=["\'](?:200|100%)["\'][^>]*?/?>', '', svg_code, flags=re.IGNORECASE)
        svg_code = re.sub(r'<rect[^>]*height=["\'](?:200|100%)["\'][^>]*width=["\'](?:200|100%)["\'][^>]*?/?>', '', svg_code, flags=re.IGNORECASE)
        svg_code = re.sub(r'style=["\'][^"\']*background[^"\']*["\']', '', svg_code, flags=re.IGNORECASE)
        svg_code = re.sub(r'width="[^"]*"', 'width="100%"', svg_code, count=1, flags=re.IGNORECASE)
        svg_code = re.sub(r'height="[^"]*"', 'height="100%"', svg_code, count=1, flags=re.IGNORECASE)
        return svg_code.replace('\n', ' ').strip()

    # On récupère les familiers des AUTRES joueurs
    bots_svgs = []
    for nom_joueur, data_joueur in db.get("utilisateurs", {}).items():
        if nom_joueur != user and data_joueur.get("familier_svg"):
            bots_svgs.append(nettoyer_svg_game(data_joueur["familier_svg"]))

    # FIX 1 : MAX 3 ENNEMIS (Tirage au sort ou génération de drones)
    if len(bots_svgs) > 3:
        bots_svgs = random.sample(bots_svgs, 3)
    elif len(bots_svgs) == 0:
        drone_rouge = "<svg viewBox='0 0 200 200' width='100%' height='100%' xmlns='[http://www.w3.org/2000/svg](http://www.w3.org/2000/svg)'><circle cx='100' cy='100' r='50' fill='#090014' stroke='#ff0055' stroke-width='6'/><circle cx='100' cy='100' r='15' fill='#00ffff'><animate attributeName='r' values='15;5;15' dur='1s' repeatCount='indefinite'/></circle><path d='M100 10 L100 40 M100 160 L100 190 M10 100 L40 100 M160 100 L190 100' stroke='#ff0055' stroke-width='6'><animateTransform attributeName='transform' type='rotate' values='0 100 100; 360 100 100' dur='4s' repeatCount='indefinite'/></path></svg>"
        bots_svgs = [drone_rouge, drone_rouge, drone_rouge] # Seulement 3 drones

    bots_json = json.dumps(bots_svgs)

    # LE MOTEUR DE JEU (Mort définitive activée)
    js_game_engine = '''
    if (window.cyberGameLoop) cancelAnimationFrame(window.cyberGameLoop);
    if (window.cyberMouseMove) window.removeEventListener("mousemove", window.cyberMouseMove);
    var oldOverlay = document.getElementById("cyber-minigame");
    if (oldOverlay) oldOverlay.remove();

    var overlay = document.createElement("div");
    overlay.id = "cyber-minigame";
    overlay.style.cssText = "position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:9998;overflow:hidden;";
    document.body.appendChild(overlay);

    var botsData = BOTS_JSON_HERE;
    var lasers = [];
    var mouseX = window.innerWidth / 2;
    var mouseY = window.innerHeight / 2;
    var dirX = 0, dirY = -1; 
    var playerHp = 100;
    var playerLastShot = 0; 

    window.cyberMouseMove = function(e) {
        var dx = e.clientX - mouseX;
        var dy = e.clientY - mouseY;
        if(Math.hypot(dx, dy) > 2) {
            var len = Math.hypot(dx, dy);
            dirX = dx/len; 
            dirY = dy/len;
        }
        mouseX = e.clientX; 
        mouseY = e.clientY;
    };
    window.addEventListener("mousemove", window.cyberMouseMove);

    var bots = botsData.map(function(svg) {
        var el = document.createElement("div");
        el.style.cssText = "position:absolute;width:80px;height:80px;transform:translate(-50%, -50%);transition: filter 0.1s;";
        el.innerHTML = svg;
        
        var hpBarContainer = document.createElement("div");
        hpBarContainer.style.cssText = "position:absolute;top:-15px;left:0;width:100%;height:6px;background:#111;border:1px solid #000;border-radius:3px;overflow:hidden;";
        var hpBar = document.createElement("div");
        hpBar.style.cssText = "width:100%;height:100%;background:#ff0055;transition:width 0.1s;box-shadow:0 0 10px #ff0055;";
        
        hpBarContainer.appendChild(hpBar);
        el.appendChild(hpBarContainer);
        overlay.appendChild(el);
        
        return {
            x: Math.random() < 0.5 ? -100 : window.innerWidth + 100,
            y: Math.random() * window.innerHeight,
            hp: 100, el: el, hpBar: hpBar, lastShot: Math.random() * 100
        };
    });

    function createExplosion(x, y, color) {
        var exp = document.createElement("div");
        exp.style.cssText = "position:absolute;left:" + x + "px;top:" + y + "px;width:150px;height:150px;background:radial-gradient(circle, #fff 0%, " + color + " 30%, transparent 100%);border-radius:50%;transform:translate(-50%,-50%);";
        overlay.appendChild(exp);
        var scale = 0, op = 1;
        var anim = setInterval(function() {
            scale += 0.25; op -= 0.1;
            exp.style.transform = "translate(-50%,-50%) scale(" + scale + ")";
            exp.style.opacity = op;
            if(op <= 0) { clearInterval(anim); exp.remove(); }
        }, 30);
    }

    function update() {
        if(!document.getElementById("cyber-game-anchor")) {
            overlay.remove();
            return;
        }

        // TIR AUTOMATIQUE
        playerLastShot++;
        if(playerLastShot > 12) { 
            var el = document.createElement("div");
            el.style.cssText = "position:absolute;left:" + mouseX + "px;top:" + mouseY + "px;width:30px;height:8px;background:#39ff14;box-shadow:0 0 20px #39ff14, 0 0 40px #ffff00;transform:translate(-50%,-50%) rotate(" + Math.atan2(dirY,dirX) + "rad);border-radius:4px;";
            overlay.appendChild(el);
            lasers.push({x: mouseX, y: mouseY, vx: dirX, vy: dirY, isPlayer: true, el: el});
            playerLastShot = 0; 
        }

        bots.forEach(function(b) {
            if(b.hp <= 0) return;
            var dx = mouseX - b.x;
            var dy = mouseY - b.y;
            var dist = Math.hypot(dx, dy);
            
            if(dist > 0) {
                b.x += (dx/dist) * 2.2; 
                b.y += (dy/dist) * 2.2;
            }
            b.el.style.left = b.x + "px";
            b.el.style.top = b.y + "px";

            b.lastShot++;
            if(b.lastShot > 70 && dist < 600) { 
                var el = document.createElement("div");
                el.style.cssText = "position:absolute;left:" + b.x + "px;top:" + b.y + "px;width:25px;height:6px;background:#ff00ff;box-shadow:0 0 20px #ff00ff;transform:translate(-50%,-50%) rotate(" + Math.atan2(dy,dx) + "rad);border-radius:3px;";
                overlay.appendChild(el);
                lasers.push({x: b.x, y: b.y, vx: dx/dist, vy: dy/dist, isPlayer: false, el: el});
                b.lastShot = 0;
            }
        });

        for(var i = lasers.length - 1; i >= 0; i--) {
            var l = lasers[i];
            l.x += l.vx * 18; 
            l.y += l.vy * 18;
            l.el.style.left = l.x + "px";
            l.el.style.top = l.y + "px";

            if(l.x < -100 || l.x > window.innerWidth + 100 || l.y < -100 || l.y > window.innerHeight + 100) {
                l.el.remove();
                lasers.splice(i, 1);
                continue;
            }

            if(l.isPlayer) {
                bots.forEach(function(b) {
                    if(b.hp > 0 && Math.hypot(b.x - l.x, b.y - l.y) < 45) {
                        b.hp -= 34;
                        b.hpBar.style.width = Math.max(0, b.hp) + "%";
                        b.el.style.filter = "brightness(3) drop-shadow(0 0 30px #ff0055)";
                        setTimeout(function() { if(b.el) b.el.style.filter="none"; }, 100);
                        l.el.remove();
                        lasers.splice(i, 1);

                        if(b.hp <= 0) {
                            createExplosion(b.x, b.y, "#ff0055");
                            b.el.remove(); // MORT DÉFINITIVE : on supprime du DOM
                        }
                    }
                });
            } else {
                if(Math.hypot(mouseX - l.x, mouseY - l.y) < 25) {
                    playerHp -= 20;
                    document.body.style.boxShadow = "inset 0 0 100px rgba(255, 0, 85, 0.9)";
                    setTimeout(function() { document.body.style.boxShadow = "none"; }, 150);
                    l.el.remove();
                    lasers.splice(i, 1);
                    
                    if(playerHp <= 0) {
                        playerHp = 100;
                        createExplosion(mouseX, mouseY, "#00ffff");
                        document.body.style.filter = "invert(1) hue-rotate(180deg)";
                        setTimeout(function() { document.body.style.filter = "none"; }, 200);
                    }
                }
            }
        }
        window.cyberGameLoop = requestAnimationFrame(update);
    }
    update();
    '''.replace("BOTS_JSON_HERE", bots_json)

    js_safe = json.dumps(js_game_engine)
    components.html(f"""
        <script>
            try {{
                var parentWindow = window.parent;
                var oldScript = parentWindow.document.getElementById('matrice-game-script');
                if(oldScript) oldScript.remove();
                
                var script = parentWindow.document.createElement('script');
                script.id = 'matrice-game-script';
                script.type = 'text/javascript';
                script.innerHTML = {js_safe};
                parentWindow.document.body.appendChild(script);
            }} catch(e) {{
                console.error("Erreur de la Matrice :", e);
            }}
        </script>
    """, height=0, width=0)

    # ==========================================
    # CSS DU BESTIAIRE
    # ==========================================
    st.markdown("""
    <style>
    .bestiaire-container { display: flex; flex-direction: column; gap: 25px; margin: 30px 0; }
    .bestiaire-card { 
        display: flex; 
        background: linear-gradient(135deg, rgba(20,0,40,0.8) 0%, rgba(5,0,16,0.95) 100%);
        border: 2px solid #ff00ff;
        border-radius: 15px;
        padding: 20px;
        align-items: center;
        box-shadow: 0 0 20px rgba(255, 0, 255, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .bestiaire-card::before {
        content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
        background: linear-gradient(to right, transparent, rgba(255,255,255,0.1), transparent);
        transform: skewX(-25deg); transition: 0.5s; pointer-events: none;
    }
    .bestiaire-card:hover::before { left: 200%; transition: 0.7s; }
    .bestiaire-card:hover {
        transform: scale(1.02) translateX(10px);
        box-shadow: -10px 0 30px #00ffff, inset 0 0 20px rgba(0, 255, 255, 0.2);
        border-color: #00ffff;
    }
    .bestiaire-rank {
        font-size: 3.5rem; font-family: 'Arial Black', sans-serif; font-style: italic;
        color: #ffff00; text-shadow: 4px 4px 0px #ff00ff; min-width: 90px; text-align: center;
    }
    .bestiaire-pet {
        width: 180px; height: 180px; display: flex; justify-content: center; align-items: center;
        margin: 0 25px; filter: drop-shadow(0 0 25px rgba(57, 255, 20, 0.6));
    }
    .bestiaire-info {
        display: flex; align-items: center; gap: 25px; flex-grow: 1;
        border-left: 3px dashed rgba(255,255,255,0.2); padding-left: 25px;
    }
    .bestiaire-avatar {
        width: 80px; height: 80px; border-radius: 12px; border: 3px solid #00ffff; image-rendering: pixelated; box-shadow: 0 0 15px #00ffff;
    }
    .bestiaire-empty-av {
        width: 80px; height: 80px; border-radius: 12px; border: 3px dashed #ff00ff; display:flex; justify-content:center; align-items:center; font-size: 2.5rem; background: #111; color: #ff00ff;
    }
    .bestiaire-name {
        font-size: 2rem; font-family: 'Arial Black', sans-serif; color: #fff; text-transform: uppercase; letter-spacing: 2px; text-shadow: 0 0 8px rgba(255,255,255,0.8); margin-bottom: 5px;
    }
    .bestiaire-score { font-size: 1.4rem; color: #39ff14; font-weight: bold; font-family: 'Courier New', monospace; text-shadow: 0 0 5px rgba(57, 255, 20, 0.5); }
    .bestiaire-badges { font-size: 1.6rem; letter-spacing: 6px; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
    # GÉNÉRATION DU BESTIAIRE (VERSION BLINDÉE)
    # ==========================================
    utilisateurs_tries = sorted(db["utilisateurs"].items(), key=lambda x: x[1].get("score", 0), reverse=True)
    html_bestiaire = "<div class='bestiaire-container'>"
    
    for index, (u_nom, u_data) in enumerate(utilisateurs_tries):
        score = round(u_data.get('score', 0), 1)
        av = u_data.get("avatar")
        img_tag = f"<img src='data:image/png;base64,{av}' class='bestiaire-avatar'>" if av else "<div class='bestiaire-empty-av'>👤</div>"
        
        fam_svg = u_data.get("familier_svg", "")
        if fam_svg:
            # 1. LE LASER ANTI-FOND : On détruit le carré noir en amont !
            fam_svg_propre = nettoyer_svg_game(fam_svg)
            
            # 2. ENCODAGE BASE64 : On transforme le monstre purifié en image stable
            b64_svg = base64.b64encode(fam_svg_propre.encode('utf-8')).decode('utf-8')
            fam_svg_display = f"<img src='data:image/svg+xml;base64,{b64_svg}' style='width:100%; height:100%; object-fit:contain;'>"
        else:
            fam_svg_display = "<div style='color:#ff0055; font-size:0.9rem; text-align:center; font-family:monospace; font-weight:bold;'>[ INCUBATION ]</div>"
            
        badges = "".join(u_data.get("badges", []))
        
        # 3. L'APLATISSEMENT : Tout sur une seule ligne pour berner le Markdown de Streamlit !
        html_bestiaire += f"<div class='bestiaire-card'><div class='bestiaire-rank'>#{index + 1}</div><div class='bestiaire-pet'>{fam_svg_display}</div><div class='bestiaire-info'>{img_tag}<div class='bestiaire-details'><div class='bestiaire-name'>{u_nom}</div><div class='bestiaire-score'>{score} PTS | {obtenir_rang(score)}</div><div class='bestiaire-badges'>{badges}</div></div></div></div>"
        
    html_bestiaire += "</div>"
    st.markdown(html_bestiaire, unsafe_allow_html=True)
    
    # 4. Historique classique des anciens marchés clos
    st.write("<br><br>", unsafe_allow_html=True)
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
    import re
    
    st.subheader("DOSSIER CLASSIFIÉ : IDENTITÉ")
    
    # Création de deux sous-onglets stylés
    tab_avatar, tab_symbiote = st.tabs(["👾 Créateur d'Avatar", "🧬 Chambre de Confinement (Symbiote)"])
    
    with tab_avatar:
        st.markdown("<p style='color:#00ffff; margin-top:10px;'>Dessine ton identité visuelle dans la matrice. Utilise les couleurs néons.</p>", unsafe_allow_html=True)
        
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
                    
    with tab_symbiote:
        st.markdown("<p style='color:#39ff14; margin-top:10px;'>Observation de l'entité cybernétique et test des capacités martiales.</p>", unsafe_allow_html=True)
        
        familier_svg = db["utilisateurs"][user].get("familier_svg", None)
        classe_fam = db["utilisateurs"][user].get("classe_familier", "Équilibré")
        attaques = db["utilisateurs"][user].get("attaques", {})
        
        if familier_svg:
            # Fonction utilitaire de nettoyage absolu (Laser anti-fond)
            def purger_svg(svg_raw):
                if not svg_raw: return ""
                s = re.sub(r'<!--.*?-->', '', svg_raw, flags=re.DOTALL)
                s = s.replace("```xml", "").replace("```html", "").replace("```", "")
                s = re.sub(r'<rect[^>]*width=["\'](?:200|100%)["\'][^>]*height=["\'](?:200|100%)["\'][^>]*?/?>', '', s, flags=re.IGNORECASE)
                s = re.sub(r'<rect[^>]*height=["\'](?:200|100%)["\'][^>]*width=["\'](?:200|100%)["\'][^>]*?/?>', '', s, flags=re.IGNORECASE)
                s = re.sub(r'style=["\'][^"\']*background[^"\']*["\']', '', s, flags=re.IGNORECASE)
                s = re.sub(r'width="[^"]*"', 'width="100%"', s, count=1, flags=re.IGNORECASE)
                s = re.sub(r'height="[^"]*"', 'height="100%"', s, count=1, flags=re.IGNORECASE)
                return s.replace('\n', ' ').strip()

            svg_propre = purger_svg(familier_svg)
            
            # Adaptation de l'aura lumineuse selon la classe (Couleur du néon)
            if "Kamikaze" in classe_fam:
                couleur_aura = "rgba(255, 0, 85, 0.7)"
                border_color = "#ff0055"
            elif "Prudent" in classe_fam:
                couleur_aura = "rgba(0, 255, 255, 0.7)"
                border_color = "#00ffff"
            else:
                couleur_aura = "rgba(57, 255, 20, 0.7)"
                border_color = "#39ff14"
            
            overlay_html = ""
            if attaques:
                st.markdown("### ⚡ Simulateur de Combat")
                choix_noms = {
                    "repos": "🧘 Repos",
                    "pierre": f"🪨 {attaques.get('pierre', {}).get('nom', 'Défense')}",
                    "feuille": f"🍃 {attaques.get('feuille', {}).get('nom', 'Zone')}",
                    "ciseaux": f"✂️ {attaques.get('ciseaux', {}).get('nom', 'Attaque')}"
                }
                
                # Le menu interactif pour allumer les attaques
# Le menu interactif pour allumer les attaques
                simul_active = st.radio("Séquence à projeter :", ["repos", "pierre", "feuille", "ciseaux"], format_func=lambda x: choix_noms[x], horizontal=True)
                
                if simul_active != "repos":
                    svg_attaque = attaques.get(simul_active, {}).get("svg_overlay", "")
                    if svg_attaque:
                        attaque_propre = purger_svg(svg_attaque)
                        
                        # --- LE VACCIN ANTI-INVISIBILITÉ & HORS-CADRE ---
                        
                        # 1. Ton intuition était la bonne : on permet aux attaques de sortir de la boîte !
                        attaque_propre = attaque_propre.replace("<svg ", "<svg overflow='visible' ")
                        
                        # 2. Le bug du Rasoir : on détruit les opacités à 0 de base pour forcer l'affichage
                        import re
                        attaque_propre = re.sub(r'opacity=["\']0["\']', 'opacity="1"', attaque_propre)
                        
                        # 3. Remplacement des arrêts sur image (freeze) par des boucles infinies
                        attaque_propre = re.sub(r'repeatCount=["\']\d+["\']', 'repeatCount="indefinite"', attaque_propre)
                        attaque_propre = re.sub(r'fill=["\']freeze["\']', 'repeatCount="indefinite"', attaque_propre)
                        
                        # Le calque d'attaque est préparé pour se superposer au monstre
                        overlay_html = f"<div style='position:absolute; top:0; left:0; width:100%; height:100%; z-index:20; filter: drop-shadow(0 0 25px {border_color});'>{attaque_propre}</div>"
            
            # ------------------------------------------------------------------------
            # FIX ANTI-BUG BLANC : Tout le HTML est collé sur une seule et même ligne
            # ------------------------------------------------------------------------
            html_showcase = f"""
            <style>
                .symbiote-showcase {{ background: radial-gradient(circle at center, #090014 0%, #000000 100%); border: 3px solid {border_color}; box-shadow: 0 0 30px {couleur_aura}, inset 0 0 60px rgba(0,0,0,0.9); border-radius: 15px; margin-top: 15px; position: relative; display: flex; justify-content: center; align-items: center; height: 450px; overflow: hidden; }}
                .symbiote-grid {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-image: linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px); background-size: 30px 30px; pointer-events: none; z-index: 1; }}
                .symbiote-tag {{ position: absolute; top: 15px; left: 20px; color: {border_color}; font-family: 'Courier New', monospace; font-weight: bold; font-size: 1.1rem; text-shadow: 0 0 10px {border_color}; z-index: 5; background: rgba(0,0,0,0.6); padding: 5px 10px; border-radius: 5px; border-left: 3px solid {border_color}; }}
                .symbiote-container {{ width: 320px; height: 320px; filter: drop-shadow(0 0 25px {border_color}); animation: float-showcase 4s cubic-bezier(0.4, 0, 0.2, 1) infinite alternate; z-index: 10; }}
                @keyframes float-showcase {{ 0% {{ transform: translateY(15px) scale(0.98); }} 100% {{ transform: translateY(-15px) scale(1.02); filter: drop-shadow(0 0 45px {border_color}); }} }}
            </style>
<div class="symbiote-showcase"><div class="symbiote-grid"></div><div class="symbiote-tag">ALIGNEMENT : {classe_fam.split(' ')[0].upper()}</div><div class="symbiote-container"><div style="position:relative; width:100%; height:100%;"><div style="position:absolute; top:0; left:0; width:100%; height:100%; z-index:10;">{svg_propre}</div>{overlay_html}</div></div></div>
            """
            st.markdown(html_showcase, unsafe_allow_html=True)
            
        else:
            st.warning("⚠️ Aucun Symbiote détecté dans vos registres. Rendez-vous à la Clinique Cybernétique pour commencer une incubation.")
elif st.session_state.page_actuelle == "🧬 Clinique Cybernétique":
    st.subheader("LABORATOIRE & FORGE MARTIALE")
    
    u_data = db["utilisateurs"][user]
    points_actuels = u_data.get("score", 0)
    brins_actuels = u_data.get("brins_adn", 0)
    niveau_actuel = obtenir_rang(points_actuels) 
    
    familier_svg = u_data.get("familier_svg", None)
    forme_historique = u_data.get("familier_desc", "Entité Inconnue")
    attaques_actuelles = u_data.get("attaques", {})
    
    st.markdown(f"<h3 style='color:#ffff00; text-shadow: 0 0 10px #ff00ff;'>🧬 Brins d'ADN disponibles : {round(brins_actuels, 1)}</h3>", unsafe_allow_html=True)
    
    col_visu, col_console = st.columns([1, 2])
    
    with col_visu:
        st.markdown("### Votre Symbiote")
        if familier_svg:
            import re
            svg_propre = re.sub(r'<!--.*?-->', '', familier_svg, flags=re.DOTALL)
            svg_propre = svg_propre.replace("```xml", "").replace("```html", "").replace("```", "").strip()
            match = re.search(r'(<svg.*?</svg>)', svg_propre, re.DOTALL | re.IGNORECASE)
            if match: svg_propre = match.group(1)
            svg_propre = svg_propre.replace("\n", " ")
            
            html_cage = f"""
            <div style="display: flex; justify-content: center; align-items: center; width: 100%; padding: 20px;">
                <div style="background: radial-gradient(circle, #1a0033 0%, #050010 80%); border: 2px solid #39ff14; box-shadow: 0 0 20px rgba(57, 255, 20, 0.3); border-radius: 15px; padding: 10px;">
                    {svg_propre}
                </div>
            </div>
            """
            st.markdown(html_cage, unsafe_allow_html=True)
        else:
            st.info("Aucune entité détectée. Utilisez le profil pour définir une base.")
            st.stop()
            
    with col_console:
        st.markdown("### ⚒️ Forge Martiale (Coût : 25 Brins)")
        st.markdown("Générez une attaque sur-mesure. **Le skin de votre symbiote ne sera pas modifié.**")
        
        choix_slot = st.selectbox("Emplacement de la technique :", ["pierre", "feuille", "ciseaux"], 
            format_func=lambda x: f"{x.upper()} (Actuel : {attaques_actuelles.get(x, {}).get('nom', 'Vide')})")
        
        nouveau_nom = st.text_input("Nom de l'attaque :", placeholder="ex: Canon Plasma, Pluie de Météores, Bouclier Divin...")
        nouvelle_desc = st.text_area("Comportement & Visuel (Sois créatif) :", placeholder="ex: [TIR / PROJECTILE] Un énorme laser rouge électrique qui traverse l'écran.\n[BOUCLIER] Une aura bleue qui pulse.")
    
        if st.button("Forger la Compétence ⚡", use_container_width=True):
            if brins_actuels < 25:
                st.error("Fonds ADN insuffisants.")
            elif len(nouveau_nom) < 3 or len(nouvelle_desc) < 5:
                st.warning("Donne un nom et une description plus détaillés pour l'Architecte.")
            else:
                placeholder_chargement = st.empty()
                html_loader = """
                <style>
                    .cyber-loader-container { border: 2px solid #00ffff; background: rgba(0,20,40,0.8); padding: 30px; border-radius: 10px; text-align: center; box-shadow: 0 0 20px #00ffff, inset 0 0 15px #00ffff; margin-bottom: 20px;}
                    .cyber-dna { font-size: 4rem; animation: spin-hammer 0.5s linear infinite; display: inline-block; filter: drop-shadow(0 0 15px #39ff14); }
                    @keyframes spin-hammer { 0% { transform: rotate(-20deg); } 50% { transform: rotate(45deg); } 100% { transform: rotate(-20deg); } }
                    .cyber-text-glitch { color: #39ff14; font-family: 'Courier New', monospace; font-size: 1.2rem; font-weight: bold; letter-spacing: 2px; animation: glitch-anim 0.2s infinite; margin-top: 15px;}
                </style>
                <div class='cyber-loader-container'><div class='cyber-dna'>⚒️</div><div class='cyber-text-glitch'>FORGE EN COURS...<br>COMPILATION DES EFFETS VISUELS</div></div>
                """
                placeholder_chargement.markdown(html_loader, unsafe_allow_html=True)
                
                # Appel du nouveau Forgeron
                reponse_brute = forger_attaque_gemini(forme_historique, choix_slot, nouveau_nom, nouvelle_desc)
                placeholder_chargement.empty()
                
                try:
                    import json
                    data_forge = json.loads(reponse_brute)
                    
                    if "svg_overlay" in data_forge:
                        # On débite et on sauvegarde uniquement l'attaque !
                        db["utilisateurs"][user]["brins_adn"] -= 25
                        if "attaques" not in db["utilisateurs"][user]:
                            db["utilisateurs"][user]["attaques"] = {}
                            
                        db["utilisateurs"][user]["attaques"][choix_slot] = {
                            "nom": data_forge["nom"],
                            "svg_overlay": data_forge["svg_overlay"]
                        }
                        
                        save_data(db)
                        trigger_animation(f"COMPÉTENCE FORGÉE : {data_forge['nom'].upper()}", jouer_son=True)
                        st.rerun()
                    else:
                        st.error("L'Architecte n'a pas renvoyé le calque SVG.")
                        st.code(reponse_brute)
                except Exception as e:
                    st.error("Échec de la forge. Le métal instable a fondu.")
                    st.code(reponse_brute)

# ==========================================
    # 🎰 LA LOTERIE MUTAGÈNE (GACHA)
    # ==========================================
    st.markdown("""<hr style="border-color: #ff00ff; border-width: 3px; border-style: dashed; margin: 40px 0;">""", unsafe_allow_html=True)
    st.subheader("🎰 LA LOTERIE ")
    
    col_gacha_info, col_gacha_btn = st.columns([1, 1])
    
    with col_gacha_info:
        st.markdown("""
        <div style="background: rgba(0,0,0,0.8); border: 2px solid #00ffff; padding: 15px; border-radius: 10px;">
            <h4 style="color: #ff00ff; margin-top: 0;">Probabilités d'Extraction :</h4>
            <ul style="list-style-type: none; padding-left: 0;">
                <li>🔵 <b>60%</b> : Échec de synthèse (Rien)</li>
                <li>🟣 <b>20%</b> : Épique (+10 Points)</li>
                <li>🟡 <b>15%</b> : Jackpot ADN (+50 Brins)</li>
                <li>🔴 <b>5%</b> : Relique Mythique (Badge 🎰)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col_gacha_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 1. LE BOUTON CACHÉ (Le vrai déclencheur Python)
        bouton_cache = st.button("EXEC_GACHA", key="btn_gacha_hidden")
        
        # 2. LE LEVIER INTERACTIF PHYSIQUE (Pure JS/HTML)
        import streamlit.components.v1 as components
        components.html("""
        <style>
            body { margin:0; display:flex; justify-content:center; align-items:center; background: transparent; user-select: none; }
            .lever-container { position: relative; width: 70px; height: 180px; background: #111; border: 4px solid #ff00ff; border-radius: 35px; box-shadow: inset 0 0 20px #000, 0 0 20px rgba(255,0,255,0.4); overflow: hidden; }
            .lever-track { position: absolute; top: 15px; bottom: 15px; left: 30px; width: 10px; background: #000; border-radius: 5px; box-shadow: inset 0 0 8px #00ffff; }
            .lever-handle { position: absolute; top: 10px; left: 1px; width: 60px; height: 60px; background: radial-gradient(circle at 30% 30%, #ff5555, #aa0000); border-radius: 50%; box-shadow: 0 0 20px #ff0055, inset -5px -5px 15px rgba(0,0,0,0.6), inset 5px 5px 15px rgba(255,255,255,0.5); cursor: grab; z-index: 10; }
            .lever-handle:active { cursor: grabbing; transform: scale(0.95); }
            .instruction { color: #00ffff; font-family: 'Arial Black', sans-serif; font-size: 1.2rem; text-align: center; margin-top: 15px; text-shadow: 0 0 10px #00ffff; text-transform: uppercase; letter-spacing: 2px; }
        </style>
        <div style="display:flex; flex-direction:column; align-items:center;">
            <div class="lever-container" id="container">
                <div class="lever-track"></div>
                <div class="lever-handle" id="knob"></div>
            </div>
            <div class="instruction" id="txt">TIRER (- 7 brins) ⬇️</div>
        </div>
        <script>
            const parentBtns = window.parent.document.querySelectorAll('button');
            parentBtns.forEach(b => {
                if(b.innerText.includes('EXEC_GACHA')) {
                    b.style.display = 'none';
                }
            });

            const knob = document.getElementById('knob');
            const txt = document.getElementById('txt');
            let isDragging = false;
            let startY = 0;
            let currentY = 10;

            knob.addEventListener('mousedown', (e) => { isDragging = true; startY = e.clientY - currentY; });
            window.addEventListener('mousemove', (e) => {
                if(!isDragging) return;
                let y = e.clientY - startY;
                if(y < 10) y = 10;
                if(y > 110) {
                    y = 110;
                    if(isDragging) {
                        isDragging = false;
                        txt.innerText = 'SYNTHÈSE...';
                        txt.style.color = '#ff00ff';
                        parentBtns.forEach(b => { if(b.innerText.includes('EXEC_GACHA')) b.click(); });
                        setTimeout(() => { knob.style.top = '10px'; currentY = 10; txt.innerText = 'TIRER (- 7 brins) ⬇️'; txt.style.color = '#00ffff'; }, 2000);
                    }
                }
                currentY = y;
                knob.style.top = y + 'px';
            });
            window.addEventListener('mouseup', () => {
                if(isDragging) {
                    isDragging = false;
                    knob.style.transition = 'top 0.3s ease';
                    knob.style.top = '10px';
                    currentY = 10;
                    setTimeout(() => knob.style.transition = '', 300);
                }
            });
        </script>
        """, height=300)

        # 3. LA LOGIQUE DU GACHA
        if bouton_cache:
            if brins_actuels < 5:
                st.error("Fonds ADN insuffisants.")
            else:
                import random
                tirage = random.random()
                if tirage < 0.60:
                    couleur = "#00f0ff" 
                    msg = "ÉCHEC DE SYNTHÈSE"
                    sub_msg = "L'ADN s'est désintégré..."
                    gain_type = "rien"
                elif tirage < 0.80:
                    couleur = "#ff00ff" 
                    msg = "ÉCLAT ÉPIQUE !"
                    sub_msg = "+10 POINTS DE SCORE"
                    gain_type = "score"
                elif tirage < 0.95:
                    couleur = "#ffff00" 
                    msg = "JACKPOT GÉNÉTIQUE !!!"
                    sub_msg = "+50 BRINS D'ADN"
                    gain_type = "adn"
                else:
                    couleur = "#ff0055" 
                    msg = "RELIQUE MYTHIQUE !!!"
                    sub_msg = "BADGE 🎰 DÉBLOQUÉ !"
                    gain_type = "badge"

                # 4. L'ANIMATION GENSHIN (Pure CSS : 0 bug, texte centré garanti)
                placeholder_gacha = st.empty()
                
                html_gacha = f"""
                <style>
                    .gacha-screen {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(5,0,16,0.98); z-index: 999999; display: flex; justify-content: center; align-items: center; overflow: hidden; }}
                    .gacha-star-head {{ position: absolute; top: -20%; left: -20%; width: 50px; height: 50px; background: white; border-radius: 50%; box-shadow: 0 0 50px 20px white, inset 0 0 20px #00ffff; animation: shooting-star 2s cubic-bezier(0.4, 0, 0.2, 1) forwards; z-index: 10; }}
                    .gacha-star-head::after {{ content: ''; position: absolute; top: 50%; right: 50%; width: 800px; height: 15px; background: linear-gradient(to left, white, rgba(255,255,255,0.4), transparent); transform: translateY(-50%) rotate(45deg); transform-origin: right center; border-radius: 10px; filter: drop-shadow(0 0 20px white); z-index: -1; }}
                    @keyframes shooting-star {{ 0% {{ top: -20%; left: -20%; filter: drop-shadow(0 0 20px white); }} 50% {{ top: 50%; left: 50%; filter: drop-shadow(0 0 80px {couleur}); background: {couleur}; box-shadow: 0 0 40px 20px {couleur}; }} 60% {{ top: 50%; left: 50%; transform: scale(0); opacity: 0; }} 100% {{ top: 50%; left: 50%; transform: scale(0); opacity: 0; }} }}
                    .gacha-flash {{ position: absolute; width: 10px; height: 10px; background: {couleur}; border-radius: 50%; opacity: 0; animation: gacha-bang 3s ease-out 1.1s forwards; box-shadow: 0 0 200px 100px {couleur}; z-index: 15; }}
                    @keyframes gacha-bang {{ 0% {{ opacity:0; transform:scale(0); }} 10% {{ opacity:1; transform:scale(80); background: white; }} 30% {{ opacity:0.8; background: {couleur}; transform:scale(150); }} 100% {{ opacity:0; transform:scale(200); }} }}
                    .gacha-result {{ position: absolute; opacity: 0; color: white; font-family: 'Arial Black', sans-serif; font-size: 5rem; text-align: center; text-transform: uppercase; animation: show-result 2s cubic-bezier(0.1, 0.9, 0.2, 1) 1.2s forwards; text-shadow: 0 0 30px {couleur}, 0 0 60px {couleur}; z-index: 20; }}
                    @keyframes show-result {{ 0% {{ opacity:0; transform: scale(0.5); }} 20% {{ opacity:1; transform: scale(1.1); }} 100% {{ opacity:1; transform: scale(1); }} }}
                    .gacha-strobe {{ position: absolute; top:0; left:0; width:100%; height:100%; background: white; opacity: 0; pointer-events: none; animation: strobe 0.2s 4 1.0s; z-index: 5; }}
                    @keyframes strobe {{ 0%, 100% {{ opacity: 0; }} 50% {{ opacity: 0.6; }} }}
                </style>
                <div class="gacha-screen">
                    <div class="gacha-strobe"></div>
                    <div class="gacha-star-head"></div>
                    <div class="gacha-flash"></div>
                    <div class="gacha-result">{msg}<br><span style="font-size: 2.5rem; color: #fff; text-shadow: 0 0 20px {couleur};">{sub_msg}</span></div>
                </div>
                """
                
                # Injection purifiée
                placeholder_gacha.markdown(html_gacha, unsafe_allow_html=True)
                
                import time
                time.sleep(6) # ⏳ Temps allongé à 6 secondes (tu as 4.5s pures pour lire le résultat !)
                placeholder_gacha.empty()
                
                # Encaissement et Récompense
                db["utilisateurs"][user]["brins_adn"] -= 7 
                
                if gain_type == "score": db["utilisateurs"][user]["score"] += 10
                elif gain_type == "adn": db["utilisateurs"][user]["brins_adn"] += 50
                elif gain_type == "badge" and "🎰" not in db["utilisateurs"][user]["badges"]: db["utilisateurs"][user]["badges"].append("🎰")
                        
                save_data(db)
                st.rerun()

elif st.session_state.page_actuelle == "⚔️ Arène":
    import json
    import base64
    import random
    import re
    import time
    import streamlit.components.v1 as components

    st.subheader("⚔️ L'ARÈNE DES SYMBIOTES (JcJ & Paris)")
    
    u_data = db["utilisateurs"].get(user, {})
    attaques_p1 = u_data.get("attaques")
    
    if not attaques_p1:
        st.warning("⚠️ Votre entité n'a pas encore de capacités de combat. Allez muter dans la Clinique Cybernétique !")
        st.stop()
        
    # --- Fonction utilitaire pour générer le code HTML de l'Arène ---
    def generer_html_combat(nom_p1, nom_p2, data_p1, data_p2, script_combat):
        def get_b64(svg_str):
            if not svg_str: return ""
            s = re.sub(r'', '', svg_str, flags=re.DOTALL)
            s = s.replace("```xml", "").replace("```html", "").replace("```", "")
            s = re.sub(r'<rect[^>]*width=["\'](?:200|100%)["\'][^>]*height=["\'](?:200|100%)["\'][^>]*?/?>', '', s, flags=re.IGNORECASE)
            s = re.sub(r'<rect[^>]*height=["\'](?:200|100%)["\'][^>]*width=["\'](?:200|100%)["\'][^>]*?/?>', '', s, flags=re.IGNORECASE)
            s = re.sub(r'style=["\'][^"\']*background[^"\']*["\']', '', s, flags=re.IGNORECASE)
            s = re.sub(r'width="[^"]*"', 'width="100%"', s, count=1, flags=re.IGNORECASE)
            s = re.sub(r'height="[^"]*"', 'height="100%"', s, count=1, flags=re.IGNORECASE)
            return "data:image/svg+xml;base64," + base64.b64encode(s.replace('\n', ' ').strip().encode('utf-8')).decode('utf-8')

        b1_base, b1_p, b1_f, b1_c = get_b64(data_p1.get("familier_svg")), get_b64(data_p1.get("attaques", {}).get("pierre", {}).get("svg_overlay")), get_b64(data_p1.get("attaques", {}).get("feuille", {}).get("svg_overlay")), get_b64(data_p1.get("attaques", {}).get("ciseaux", {}).get("svg_overlay"))
        b2_base, b2_p, b2_f, b2_c = get_b64(data_p2.get("familier_svg")), get_b64(data_p2.get("attaques", {}).get("pierre", {}).get("svg_overlay")), get_b64(data_p2.get("attaques", {}).get("feuille", {}).get("svg_overlay")), get_b64(data_p2.get("attaques", {}).get("ciseaux", {}).get("svg_overlay"))
        
        script_json = json.dumps(script_combat)
        return f"""
        <!DOCTYPE html><html><head><style>
            @import url('[https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap](https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap)');
            body {{ margin: 0; padding: 0; background-color: #050010; color: white; font-family: 'Courier Prime', monospace; overflow: hidden; }}
            .arena-container {{ position: relative; width: 100vw; height: 450px; background: radial-gradient(circle at center, #1a0033 0%, #000 100%); border: 3px solid #ff00ff; overflow: hidden; box-shadow: inset 0 0 50px rgba(255,0,255,0.2); }}
            .grid {{ position: absolute; width: 100%; height: 100%; background-image: linear-gradient(rgba(0,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,255,0.1) 1px, transparent 1px); background-size: 40px 40px; transform: perspective(500px) rotateX(60deg); transform-origin: bottom; opacity: 0.5; bottom: -20%; }}
            .hud {{ position: absolute; top: 20px; width: 100%; display: flex; justify-content: space-between; padding: 0 40px; box-sizing: border-box; z-index: 10; }}
            .hp-box {{ background: rgba(0,0,0,0.8); border: 2px solid #00ffff; padding: 10px 20px; border-radius: 5px; box-shadow: 0 0 10px #00ffff; }}
            .hp-name {{ font-weight: bold; font-size: 1.2rem; margin-bottom: 8px; text-transform: uppercase; color: #fff; }}
            .dot-container {{ display: flex; gap: 15px; }} .dot {{ width: 20px; height: 20px; border-radius: 50%; background: #111; border: 2px solid #444; transition: all 0.3s ease; }}
            .stage {{ position: absolute; bottom: 80px; width: 100%; display: flex; justify-content: space-between; padding: 0 100px; box-sizing: border-box; z-index: 5; }}
            .fighter {{ position: relative; width: 160px; height: 160px; display: flex; justify-content: center; align-items: center; filter: drop-shadow(0 0 15px rgba(255,255,255,0.2)); transition: transform 0.2s; }}
            .base-sprite {{ position: absolute; width: 100%; height: 100%; object-fit: contain; z-index: 1; }}
            .overlay-sprite {{ position: absolute; top:0; left:0; width: 100%; height: 100%; object-fit: contain; z-index: 2; opacity: 0; transition: opacity 0.3s; filter: drop-shadow(0 0 25px #00ffff); }}
            .dialogue-box {{ position: absolute; bottom: 0; width: 100%; height: 80px; background: rgba(0,20,40,0.9); border-top: 3px solid #00ffff; display: flex; align-items: center; padding: 0 20px; font-size: 1.1rem; font-weight: bold; color: #00ffff; text-shadow: 0 0 5px #00ffff; box-sizing: border-box; }}
            .anim-dash-p1 {{ animation: dash-right 0.6s cubic-bezier(0.25, 1, 0.5, 1); z-index: 10; }} .anim-dash-p2 {{ animation: dash-left 0.6s cubic-bezier(0.25, 1, 0.5, 1); z-index: 10; }}
            @keyframes dash-right {{ 0% {{ transform: translateX(0); }} 50% {{ transform: translateX(350px) scale(1.2); filter: drop-shadow(0 0 40px #00ffff); }} 100% {{ transform: translateX(0); }} }}
            @keyframes dash-left {{ 0% {{ transform: translateX(0); }} 50% {{ transform: translateX(-350px) scale(1.2); filter: drop-shadow(0 0 40px #ff00ff); }} 100% {{ transform: translateX(0); }} }}
            .anim-hit {{ animation: shake-hit 0.4s ease; filter: drop-shadow(0 0 50px red) brightness(2) !important; }}
            @keyframes shake-hit {{ 0%, 100% {{ transform: translateX(0); }} 20% {{ transform: translateX(-15px) rotate(-10deg); }} 40% {{ transform: translateX(15px) rotate(10deg); }} 60% {{ transform: translateX(-10px); }} 80% {{ transform: translateX(10px); }} }}
            .anim-screen-shake {{ animation: global-shake 0.5s cubic-bezier(.36,.07,.19,.97) both; }}
            @keyframes global-shake {{ 10%, 90% {{ transform: translate3d(-5px, 5px, 0); }} 20%, 80% {{ transform: translate3d(10px, -5px, 0); }} 30%, 50%, 70% {{ transform: translate3d(-15px, 10px, 0); }} 40%, 60% {{ transform: translate3d(15px, -10px, 0); }} }}
            .anim-ko {{ animation: fade-out-ko 2s forwards; filter: grayscale(1) brightness(0) !important; }}
            @keyframes fade-out-ko {{ 100% {{ opacity:0; transform: translateY(50px) scale(0.5); }} }}
        </style></head><body>
        <div class="arena-container" id="arena"><div class="grid"></div><div class="hud">
            <div class="hp-box"><div class="hp-name">{nom_p1}</div><div class="dot-container" style="justify-content:flex-start;"><div class="dot" id="p1-dot-1"></div><div class="dot" id="p1-dot-2"></div><div class="dot" id="p1-dot-3"></div></div></div>
            <div class="hp-box" style="border-color:#ff00ff; box-shadow:0 0 10px #ff00ff;"><div class="hp-name" style="text-align:right;">{nom_p2}</div><div class="dot-container" style="justify-content:flex-end;"><div class="dot" id="p2-dot-1"></div><div class="dot" id="p2-dot-2"></div><div class="dot" id="p2-dot-3"></div></div></div>
        </div>
        <div class="stage">
            <div class="fighter" id="p1"><img src="{b1_base}" class="base-sprite"><img src="{b1_p}" class="overlay-sprite" id="p1-pierre"><img src="{b1_f}" class="overlay-sprite" id="p1-feuille"><img src="{b1_c}" class="overlay-sprite" id="p1-ciseaux"></div>
            <div class="fighter" id="p2" style="transform: scaleX(-1);"><img src="{b2_base}" class="base-sprite"><img src="{b2_p}" class="overlay-sprite" id="p2-pierre"><img src="{b2_f}" class="overlay-sprite" id="p2-feuille"><img src="{b2_c}" class="overlay-sprite" id="p2-ciseaux"></div>
        </div>
        <div class="dialogue-box" id="dialogue">Initialisation système... CLIQUEZ ICI POUR LANCER L'ASSAUT.</div></div>
        <script>
            const scriptJson = {script_json}; const dialogue = document.getElementById('dialogue'); const p1 = document.getElementById('p1'); const p2 = document.getElementById('p2'); const arena = document.getElementById('arena');
            let scoreP1 = 0; let scoreP2 = 0; let started = false;
            function typeWriter(text, i, cb) {{ if (i===0) dialogue.innerHTML=""; if (i<text.length) {{ dialogue.innerHTML+=text.charAt(i); setTimeout(()=>typeWriter(text, i+1, cb), 20); }} else if (cb) cb(); }}
            function sleep(ms) {{ return new Promise(resolve => setTimeout(resolve, ms)); }}
            async function playTurn(tour) {{ return new Promise(resolve => {{ typeWriter(tour.texte, 0, async () => {{
                let over1 = document.getElementById('p1-' + tour.p1_move); let over2 = document.getElementById('p2-' + tour.p2_move);
                if(over1) over1.style.opacity = 1; if(over2) over2.style.opacity = 1; await sleep(600); 
                let dot1 = document.getElementById('p1-dot-' + tour.tour); let dot2 = document.getElementById('p2-dot-' + tour.tour);
                if(tour.winner === 1) {{ p1.classList.add('anim-dash-p1'); await sleep(300); p2.classList.add('anim-hit'); arena.classList.add('anim-screen-shake'); dot1.style.background = '#39ff14'; dot1.style.borderColor = '#39ff14'; dot1.style.boxShadow = '0 0 15px #39ff14'; dot2.style.background = '#ff0055'; dot2.style.borderColor = '#ff0055'; dot2.style.boxShadow = '0 0 15px #ff0055'; scoreP1++; }} 
                else if (tour.winner === 2) {{ p2.classList.add('anim-dash-p2'); await sleep(300); p1.classList.add('anim-hit'); arena.classList.add('anim-screen-shake'); dot1.style.background = '#ff0055'; dot1.style.borderColor = '#ff0055'; dot1.style.boxShadow = '0 0 15px #ff0055'; dot2.style.background = '#39ff14'; dot2.style.borderColor = '#39ff14'; dot2.style.boxShadow = '0 0 15px #39ff14'; scoreP2++; }} 
                else {{ p1.classList.add('anim-dash-p1'); p2.classList.add('anim-dash-p2'); await sleep(300); p1.classList.add('anim-hit'); p2.classList.add('anim-hit'); arena.classList.add('anim-screen-shake'); dot1.style.background = '#eab308'; dot1.style.borderColor = '#eab308'; dot1.style.boxShadow = '0 0 10px #eab308'; dot2.style.background = '#eab308'; dot2.style.borderColor = '#eab308'; dot2.style.boxShadow = '0 0 10px #eab308'; }}
                await sleep(600); if(over1) over1.style.opacity = 0; if(over2) over2.style.opacity = 0; p1.className = "fighter"; p2.className = "fighter"; arena.className = "arena-container"; await sleep(500); resolve();
            }}); }}); }}
            async function startBattle() {{ if(started) return; started = true;
                for(let i=0; i<scriptJson.length; i++) {{ dialogue.innerHTML = "=== ROUND " + scriptJson[i].tour + " ==="; await sleep(800); await playTurn(scriptJson[i]); }}
                if(scoreP1 > scoreP2) {{ typeWriter("VICTOIRE DE {nom_p1} ! Le symbiote ennemi est anéanti.", 0); p2.classList.add('anim-ko'); }} 
                else if (scoreP2 > scoreP1) {{ typeWriter("VICTOIRE DE {nom_p2} ! Entité abattue.", 0); p1.classList.add('anim-ko'); }} 
                else {{ typeWriter("ÉGALITÉ PARFAITE. Aucun ascendant tactique.", 0); p1.classList.add('anim-ko'); p2.classList.add('anim-ko'); }}
            }}
            document.getElementById('arena').addEventListener('click', startBattle);
        </script></body></html>
        """

    # ==========================================
    # AFFICHAGE DU COMBAT EN DIRECT (Si on vient de l'accepter)
    # ==========================================
    if st.session_state.get("combat_direct_html"):
        st.markdown("<h2 style='color:#39ff14; text-align:center;'>⚔️ RÉSULTAT DE L'AFFRONTEMENT ⚔️</h2>", unsafe_allow_html=True)
        components.html(st.session_state.combat_direct_html, height=450)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("QUITTER LE RING 🚀", use_container_width=True):
            st.session_state.combat_direct_html = None
            st.rerun()
        st.stop()

    choix = {"pierre": f"🪨 {attaques_p1.get('pierre', {}).get('nom', 'Blocage')}", "feuille": f"🍃 {attaques_p1.get('feuille', {}).get('nom', 'Zone')}", "ciseaux": f"✂️ {attaques_p1.get('ciseaux', {}).get('nom', 'Lame')}"}

    # ==========================================
    # 1. FIL D'ACTUALITÉ DE L'ARÈNE (Les défis ouverts)
    # ==========================================
    st.markdown("### 📜 Fil d'Actualité des Combats")
    combats_ouverts = [q for q in db["questions"] if q.get("type") == "combat" and q["statut"] == "ouvert"]
    
    if not combats_ouverts:
        st.info("Aucun duel en attente sur la Matrice. Vous pouvez lancer un assaut ci-dessous.")
    
    for q in combats_ouverts:
        att = q["attaquant"]
        dfn = q["defenseur"]
        
        with st.expander(f"⚔️ {q['titre']} - En attente de {dfn}"):
            if user == dfn:
                st.markdown(f"**{att}** vous a provoqué en duel ! Choisissez vos 3 parades pour riposter et clore le marché.")
                c1, c2, c3 = st.columns(3)
                deck_def = []
                with c1: deck_def.append(st.selectbox("Tour 1", ["pierre", "feuille", "ciseaux"], format_func=lambda x: choix[x], key=f"d1_{q['id']}"))
                with c2: deck_def.append(st.selectbox("Tour 2", ["pierre", "feuille", "ciseaux"], format_func=lambda x: choix[x], key=f"d2_{q['id']}"))
                with c3: deck_def.append(st.selectbox("Tour 3", ["pierre", "feuille", "ciseaux"], format_func=lambda x: choix[x], key=f"d3_{q['id']}"))
                
                # Le défenseur doit aussi parier !
                choix_pari_def = st.selectbox("Qui va gagner ce bain de sang ?", q["choix"], key=f"def_choix_{q['id']}")
                cred_def = st.slider("Votre crédence (%)", 0, 100, 100, key=f"def_cred_{q['id']}")
                
                if st.button("ACCEPTER LE DÉFI ET COMBATTRE ⚡", key=f"btn_acc_{q['id']}"):
                    # 1. Enregistrement du pari
                    db["paris"].append({"id_question": q["id"], "joueur": user, "credences": {c: (cred_def if c == choix_pari_def else (100-cred_def)/2) for c in q["choix"]}, "mise": 0})
                    
                    # 2. Résolution du combat
                    victoires = {"pierre": "ciseaux", "feuille": "pierre", "ciseaux": "feuille"}
                    deck_att = q["deck_attaquant"]
                    data_att = db["utilisateurs"][att]
                    
                    script_combat = []
                    s_att, s_def = 0, 0
                    
                    for i in range(3):
                        c_a = deck_att[i]
                        c_d = deck_def[i]
                        n_a = data_att.get("attaques", {}).get(c_a, {}).get("nom", c_a).upper()
                        n_d = attaques_p1.get(c_d, {}).get("nom", c_d).upper()
                        
                        if c_a == c_d:
                            v = 0; txt = f"CHOC ! [{n_a}] annule [{n_d}] !"
                        elif victoires[c_a] == c_d:
                            v = 1; txt = f"BIM ! [{n_a}] détruit [{n_d}] !"; s_att += 1
                        else:
                            v = 2; txt = f"AÏE ! [{n_d}] écrase [{n_a}] !"; s_def += 1
                            
                        script_combat.append({"tour": i+1, "p1_move": c_a, "p2_move": c_d, "winner": v, "texte": txt, "dmg1": 0, "dmg2": 0})
                    
                    if s_att > s_def: q["resultat"] = f"Victoire {att}"
                    elif s_def > s_att: q["resultat"] = f"Victoire {dfn}"
                    else: q["resultat"] = "Égalité"
                    
                    q["statut"] = "clos"
                    
                    # On génère l'HTML final et on le stocke dans le marché pour que les parieurs puissent le voir !
                    html_final = generer_html_combat(att, dfn, data_att, u_data, script_combat)
                    q["html_combat"] = html_final
                    
                    # Le défenseur le voit en direct, donc on le met dans son historique vu
                    db["utilisateurs"][user]["historique_vu"].append(q["id"])
                    
                    save_data(db)
                    st.session_state.combat_direct_html = html_final
                    st.rerun()
            else:
                pari_existant = next((p for p in db["paris"] if p["id_question"] == q["id"] and p["joueur"] == user), None)
                if pari_existant:
                    st.success("🎫 Ticket de pari enregistré pour ce combat. En attente du défenseur...")
                else:
                    st.markdown("🎲 **Les paris sont ouverts pour ce duel !**")
                    choix_pari = st.selectbox("Qui va gagner ?", q["choix"], key=f"spec_choix_{q['id']}")
                    cred = st.slider("Votre crédence (%)", 0, 100, 50, key=f"spec_cred_{q['id']}")
                    if st.button("VALIDER LE PARI", key=f"btn_spec_{q['id']}"):
                        db["paris"].append({"id_question": q["id"], "joueur": user, "credences": {c: (cred if c == choix_pari else (100-cred)/2) for c in q["choix"]}, "mise": 0})
                        save_data(db)
                        st.success("Pari validé !")
                        st.rerun()

    st.markdown("---")
    
    # ==========================================
    # 2. LANCER UN ASSAUT
    # ==========================================
    st.markdown("### ⚔️ Organiser un Assaut")
    adversaires_valides = [k for k, v in db["utilisateurs"].items() if k != user and "attaques" in v]
    
    if not adversaires_valides:
        st.info("Aucun adversaire génétiquement modifié n'est disponible.")
        st.stop()
        
    adv_nom = st.selectbox("Cible de l'assaut :", adversaires_valides)
    
    st.write(f"Saisissez votre séquence d'attaque aveugle contre **{adv_nom}** :")
    colA, colB, colC = st.columns(3)
    deck_attaque = []
    with colA: deck_attaque.append(st.selectbox("Atk Tour 1", ["pierre", "feuille", "ciseaux"], format_func=lambda x: choix[x], key="a1"))
    with colB: deck_attaque.append(st.selectbox("Atk Tour 2", ["pierre", "feuille", "ciseaux"], format_func=lambda x: choix[x], key="a2"))
    with colC: deck_attaque.append(st.selectbox("Atk Tour 3", ["pierre", "feuille", "ciseaux"], format_func=lambda x: choix[x], key="a3"))
    
    st.markdown("#### 🎲 Mise Initiale (Obligatoire)")
    options_victoire = [f"Victoire {user}", f"Victoire {adv_nom}", "Égalité"]
    choix_att = st.selectbox("Sur quelle issue pariez-vous ?", options_victoire)
    cred_att = st.slider("Votre crédence sur cette issue (%)", 0, 100, 100)
    
    if st.button("⚡ LANCER LE DÉFI ET OUVRIR LE MARCHÉ ⚡", use_container_width=True):
        combat_id = f"combat_{int(time.time())}"
        
        # Création du marché
        nouvelle_question = {
            "id": combat_id,
            "titre": f"ASSAUT : {user} attaque {adv_nom} !",
            "type": "combat",
            "statut": "ouvert",
            "attaquant": user,
            "defenseur": adv_nom,
            "deck_attaquant": deck_attaque,
            "choix": options_victoire,
            "resultat": None
        }
        db["questions"].append(nouvelle_question)
        
        # Création du pari de l'attaquant
        db["paris"].append({
            "id_question": combat_id,
            "joueur": user,
            "credences": {c: (cred_att if c == choix_att else (100-cred_att)/2) for c in options_victoire},
            "mise": 0
        })
        
        save_data(db)
        st.success(f"Défi lancé ! Le marché est ouvert sur la tête de {adv_nom}.")
        st.rerun()
