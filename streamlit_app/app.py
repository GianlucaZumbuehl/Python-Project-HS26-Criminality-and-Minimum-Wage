# SEITE 1: Resultate und Diskussion
# Starten im Terminal:
#   cd streamlit_app
#   streamlit run app.py

import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import funktionen as f

st.set_page_config(page_title="Results", layout="wide")

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
# Uhr oben rechts
# ------------------------------------------------------------


@st.fragment(run_every=10)
def uhr():
    jetzt = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%H:%M")
    st.markdown(f"<p style='text-align:right; font-size: 1.5rem;'>{jetzt}</p>",
                unsafe_allow_html=True)


uhr()

df = f.daten_laden()

st.title("Minimum Wage and Crime in Swiss Cantons")


# ------------------------------------------------------------
# 1. Was machen wir?
# ------------------------------------------------------------
st.header("1. What we do")
st.write("Switzerland is a federal state with the subsidiarity Principe. This means that what is not written as task in the higher instance is in the next lower instance and so on. One of these themes is minimum wage. In Switzerland there is no national minimum wage Instead, the cantons of Neuchâtel, Jura, Ticino, Geneva and Basel-Stadt have introduced their own minimum wages. Recently also some communes determine own minimum wages like Luzern since January 2026 and in Zurich from January 2027. Minimum wages are a political Newland and only court judgements have cleared this recently, for cantons in 2017. (quelle1) and communes in may 2026 (quelle 2)."

         "Interestingly, minimum wages in Switzerland are seen as an interference with economic freedom, which is not permitted. Therefore, minimum wages are only permitted as a social policy measure. While they can be used to combat poverty, they cannot be employed as an economic policy instrument to regulate wages. This means they must be set at a relatively low level."

         "People in the low-wage sector who struggle with the high living standards in Switzerland should benefit most from this. We therefore asked ourselves how this effect could be measured. We though that an increase in wages could reduce the shoplifting rate, which often happens spontaneously, and often relate to everyday consumer goods. This leads us to our research question: Do minimum wages influence shoplifting by 20- to 29-year-olds?"

         "We focus on this age group because young Adults starting out their career, are particularly likely to work in low-paid sectors like, retail or gastronomy industry, and therefore are often directly affected by minimum wage.")


# ------------------------------------------------------------
# 2. Daten und Data Cleaning
# ------------------------------------------------------------
st.header("2. Data and Data Cleaning")
st.write("PLATZHALTER: Woher kommen die Daten (BFS Polizeiliche Kriminalstatistik, Bevölkerung)?")
st.write("PLATZHALTER: Wie wurden die Daten bereinigt und zusammengeführt?")


# ------------------------------------------------------------
# 3. Ausgewählte Kantone
# ------------------------------------------------------------
st.header("3. Selected Cantons")
st.write("PLATZHALTER: Warum diese Mindestlohn Kantone und warum diese Kontrollkantone?")

# Übersicht aus den Einstellungen in funktionen.py (nur Anzeige)
uebersicht = pd.DataFrame({
    "Canton with minimum wage": list(f.EINFUEHRUNG),
    "Introduced": list(f.EINFUEHRUNG.values()),
    "First full year": list(f.ERSTES_VOLLES_JAHR.values()),
    "Control cantons": [", ".join(f.KONTROLLEN[k]) for k in f.EINFUEHRUNG],
})
st.dataframe(uebersicht, hide_index=True)


# ------------------------------------------------------------
# 4. Parallel Trends
# ------------------------------------------------------------
st.header("4. Parallel Trends")
st.write("PLATZHALTER: Welche Kontrollkantone haben die stärksten parallelen Trends?")

tab1, tab2, tab3 = st.tabs(["Neuenburg", "Genf", "Basel-Stadt"])
with tab1:
    st.pyplot(f.grafik_trends(df, "Neuenburg", f.KONTROLLEN["Neuenburg"]))
with tab2:
    st.pyplot(f.grafik_trends(df, "Genf", f.KONTROLLEN["Genf"]))
with tab3:
    st.pyplot(f.grafik_trends(df, "Basel-Stadt", f.KONTROLLEN["Basel-Stadt"]))


# ------------------------------------------------------------
# 5. Resultate: Regressionen und Event Study
# ------------------------------------------------------------
st.header("5. Results")
st.write("PLATZHALTER: Kurze Erklärung der Regression.")

tab1, tab2, tab3 = st.tabs(["Neuenburg", "Genf", "Basel-Stadt"])
for tab, kanton in [(tab1, "Neuenburg"), (tab2, "Genf"), (tab3, "Basel-Stadt")]:
    with tab:
        kontrollen = f.KONTROLLEN[kanton]

        links, rechts = st.columns(2)
        links.subheader("DiD")
        links.pyplot(f.grafik_did(df, kanton, kontrollen))
        rechts.subheader("Event Study")
        rechts.pyplot(f.grafik_event_study(df, kanton, kontrollen))

        st.subheader("Regression Table")
        st.dataframe(f.did_tabelle(df, kanton, kontrollen), hide_index=True)
        st.caption("* p < 0.1   ** p < 0.05   *** p < 0.01")


# ------------------------------------------------------------
# 6. Interpretation und Diskussion
# ------------------------------------------------------------
st.header("6. Interpretation and Discussion")

st.subheader("Interpretation")
st.write("PLATZHALTER: Was bedeuten die Resultate pro Kanton?")

st.subheader("Significance")
st.write("PLATZHALTER: Wie sicher sind die Resultate?")


# ------------------------------------------------------------
# 7. Limitationen
# ------------------------------------------------------------
st.header("7. Limitations")
st.write("PLATZHALTER: Was man mit den Resultaten anfangen kann und was nicht. "
         "Zum Beispiel kleine Fallzahlen, nur ein behandelter Kanton pro Schätzung, "
         "andere Massnahmen zur gleichen Zeit, Ladendiebstahl nur auf Antrag verfolgt.")
