# GEMEINSAMES LAYOUT für alle Seiten
# Hier werden Design (CSS), Datum/Uhrzeit und Footer an einem Ort festgelegt.

import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

UZH_BLAU = "#0028A5"


# ------------------------------------------------------------
# Design: Breite, Seitentitel, Blocksatz
# ------------------------------------------------------------
def stil():
    st.markdown(f"""
    <style>
    /* Inhalt zentriert mit maximaler Breite (besser lesbar auf grossen Bildschirmen) */
    [data-testid="stMainBlockContainer"] {{max-width: 1100px; margin: 0 auto;}}
    h1, h2 {{text-align: center;}}

    /* Untertitel: linksbündig und kleiner */
    h3 {{text-align: left; font-size: 1.2rem !important;}}

    /* Beschriftungen der Auswahlfelder: fett, so gross wie normaler Text */
    [data-testid="stWidgetLabel"] p {{font-weight: 700 !important; font-size: 1rem !important;}}

    /* Seitentitel in UZH-Blau und fett */
    h1 {{color: {UZH_BLAU} !important; font-weight: 700 !important;}}

    /* Seitenauswahl oben grösser */
    [data-testid="stTopNavLink"] span, [data-testid="stTopNavLink"] p {{font-size: 1.25rem !important;}}

    /* Fliesstext im Blocksatz mit Silbentrennung */
    [data-testid="stMarkdownContainer"] p {{
        text-align: justify;
        hyphens: auto;
        -webkit-hyphens: auto;
    }}
    </style>
    """, unsafe_allow_html=True)


# ------------------------------------------------------------
# Datum und Uhrzeit oben rechts (Zeitzone der Besucherin / des Besuchers)
# ------------------------------------------------------------
@st.fragment(run_every=10)
def uhr():
    try:
        zone = ZoneInfo(st.context.timezone or "Europe/Zurich")
    except Exception:
        zone = ZoneInfo("Europe/Zurich")  # falls der Browser keine Zeitzone liefert
    jetzt = datetime.now(zone).strftime("%d.%m.%Y&nbsp;&nbsp;&nbsp;%H:%M")
    st.markdown(f"<p style='text-align:right; font-size: 1.5rem;'>{jetzt}</p>",
                unsafe_allow_html=True)


# ------------------------------------------------------------
# Footer (nicht auf der Startseite verwenden)
# ------------------------------------------------------------
def footer():
    st.divider()
    st.markdown("""
    <p style='text-align:center; color:#555555; font-size:0.9rem;'>
    PLATZHALTER: Namen der Gruppe<br>
    PLATZHALTER: Python Seminar HS 2026, Universität Zürich<br>
    PLATZHALTER: Datenquellen (z.&nbsp;B. BFS Polizeiliche Kriminalstatistik)
    </p>
    """, unsafe_allow_html=True)
