
# Code von Caner
# SEITE 2: Interaktiv (Caner)
# Die Person wählt selbst einen Mindestlohn-Kanton und Kontrollkantone.
# Danach werden DiD und Event Study für diese Auswahl berechnet.

import streamlit as st
import funktionen as f
import layout

st.set_page_config(page_title="Interactive", layout="wide")

layout.stil()
layout.uhr()


df = f.daten_laden()
# Grafik zentriert anzeigen: mittlere Spalte = 4/6 der Seitenbreite
# Grafik zentriert anzeigen. "mitte" = Breite der mittleren Spalte (links und rechts je 1)


def zeige_grafik(fig, mitte=10):
    links, spalte, rechts = st.columns([1, mitte, 1])
    spalte.pyplot(fig)


st.title("Try it yourself!", anchor=False)
st.write("Choose a canton with a minimum wage and one or more control cantons. "
         "The analyses below are calculated directly from the data for your selection.")


# ------------------------------------------------------------
# 1. Auswahl
# ------------------------------------------------------------
st.header("1. Your selection", anchor=False)


# Farben der Auswahl: Mindestlohn-Kanton hellblau, Kontrollkantone hellorange (wie in der DiD-Grafik)
st.markdown("""
<style>
.st-key-kanton button[data-selected="true"],
.st-key-kanton [data-testid="stBaseButton-pillsActive"] {
    background-color: #d6e0f5 !important;
    border-color: #0028A5 !important;
}
.st-key-kontrollen button[data-selected="true"],
.st-key-kontrollen [data-testid="stBaseButton-pillsActive"] {
    background-color: #fde2d2 !important;
    border-color: #E8732A !important;
}
.st-key-kanton button[data-selected="true"] *,
.st-key-kontrollen button[data-selected="true"] * {
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

# Mindestlohn-Kanton (nur die drei aus unserer Analyse), genau einer wählbar
kanton = st.pills(
    "Choose canton with minimum wage",
    options=list(f.EINFUEHRUNG),
    selection_mode="single",
    default="Neuenburg",
    key="kanton",
)

# Kontrollkantone: alle Kantone ohne Mindestlohn, mehrere wählbar
moegliche_kontrollen = sorted(
    k for k in df["Canton"].unique() if k not in f.EINFUEHRUNG)

kontrollen = st.pills(
    "Control cantons (click to select or deselect)",
    options=moegliche_kontrollen,
    selection_mode="multi",
    default=[],
    key="kontrollen",
)

# Ohne Mindestlohn-Kanton keine Analyse möglich
if kanton is None:
    st.info("Please choose a canton with minimum wage.")
    st.stop()

st.caption(f"Minimum wage introduced in {f.EINFUEHRUNG[kanton]} "
           f"(first full year: {f.ERSTES_VOLLES_JAHR[kanton]}).")

# Ohne Kontrollkanton keine Analyse möglich
if len(kontrollen) == 0:
    st.info("Please choose at least one control canton.")
    st.stop()
# ------------------------------------------------------------
# 2. Parallel Trends (Funktion aus funktionen.py)
# ------------------------------------------------------------
st.header("2. Parallel Trends", anchor=False)

# Zeige_grafik zentriert einfach grafik, nur f.grafik_trend => nicht zentriert
zeige_grafik(f.grafik_trends(df, kanton, kontrollen))
zeige_grafik(f.grafik_trends_durchschnitt(df, kanton, kontrollen))
# ------------------------------------------------------------
# 3. Difference-in-Differences
# ------------------------------------------------------------
st.header("3. Difference-in-Differences", anchor=False)

zeige_grafik(f.grafik_did(df, kanton, kontrollen))

# Tabelle: Zahlen formatieren, Schrift grösser, ohne Index
tabelle = f.did_tabelle(df, kanton, kontrollen)
st.table(
    tabelle.style
    .format({"β3 (log)": "{:.3f}", "Std. error": "{:.3f}", "p-value": "{:.5f}",
             "R²": "{:.3f}", "Effect in %": "{:.1f}", "N": "{:d}"})
    .set_properties(**{"font-size": "1.2rem"})
    .hide(axis="index")
)
st.caption("Standard errors: HC1 (robust).")


# ------------------------------------------------------------
# 4. Event Study
# ------------------------------------------------------------
st.header("4. Event Study", anchor=False)

zeige_grafik(f.grafik_event_study(df, kanton, kontrollen))


layout.footer()
