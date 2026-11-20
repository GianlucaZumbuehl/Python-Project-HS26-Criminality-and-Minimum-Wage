# SEITE 2: Interaktiv
# Streamlit zeigt jede Datei im Ordner "pages" automatisch als eigene Seite an.

import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import funktionen as f

st.set_page_config(page_title="Interactive", layout="wide")

website_title_color = "#0028A5"
chapter_title_color = "#000000"
small_title_color = "#000000"
title_graph_color = "#000000"

st.markdown(f"""
<style>
h1 {{color: {website_title_color} !important;}}
h2 {{color: {chapter_title_color} !important;}}
h3 {{color: {small_title_color} !important;}}
[data-testid="stWidgetLabel"] p {{color: {title_graph_color} !important;}}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# Uhr oben rechts (Stunden und Minuten)
# ------------------------------------------------------------
@st.fragment(run_every=10)
def uhr():
    jetzt = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%H:%M")
    st.markdown(f"<p style='text-align:right; font-size:0.8rem;'>Zurich {jetzt}</p>",
                unsafe_allow_html=True)

uhr()

df = f.daten_laden()

st.title("Interactive Analysis")

# Auswahl: einmal wählen, dann auf den Knopf drücken
with st.form("auswahl"):
    kanton = st.selectbox("Canton with minimum wage", [
                          "Neuenburg", "Genf", "Basel-Stadt"])

    alle_kontrollen = sorted(df["Canton"].unique())
    for k in ["Neuenburg", "Genf", "Basel-Stadt"]:
        alle_kontrollen.remove(k)
    kontrollen = st.multiselect("Control cantons", alle_kontrollen)

    knopf = st.form_submit_button("Compare")

# Erst weitermachen, wenn der Knopf gedrückt wurde
if not knopf:
    st.stop()

# Keine Kontrollen gewählt: Standard aus funktionen.py nehmen
if kontrollen == []:
    kontrollen = f.KONTROLLEN[kanton]

st.write("Kontrollen:", ", ".join(kontrollen))

st.header("Parallel Trends")
st.pyplot(f.grafik_trends(df, kanton, kontrollen))

st.header("Event Study")
st.pyplot(f.grafik_event_study(df, kanton, kontrollen))

st.header("Difference in Differences")
st.pyplot(f.grafik_did(df, kanton, kontrollen))
st.dataframe(f.did_tabelle(df, kanton, kontrollen), hide_index=True)
st.caption("* p < 0.1   ** p < 0.05   *** p < 0.01")
