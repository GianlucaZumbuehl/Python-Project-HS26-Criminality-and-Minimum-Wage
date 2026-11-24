
## CODE VON GIAN LUCA
# # SEITE 2: Interaktiv
# # Streamlit zeigt jede Datei im Ordner "pages" automatisch als eigene Seite an.

# import streamlit as st
# from datetime import datetime
# from zoneinfo import ZoneInfo
# import funktionen as f

# st.set_page_config(page_title="Interactive", layout="wide")

# website_title_color = "#0028A5"
# chapter_title_color = "#000000"
# small_title_color = "#000000"
# title_graph_color = "#000000"

# st.markdown(f"""
# <style>
# h1 {{color: {website_title_color} !important;}}
# h2 {{color: {chapter_title_color} !important;}}
# h3 {{color: {small_title_color} !important;}}
# [data-testid="stWidgetLabel"] p {{color: {title_graph_color} !important;}}
# </style>
# """, unsafe_allow_html=True)

# # ------------------------------------------------------------
# # Uhr oben rechts (Stunden und Minuten)
# # ------------------------------------------------------------
# @st.fragment(run_every=10)
# def uhr():
#     jetzt = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%H:%M")
#     st.markdown(f"<p style='text-align:right; font-size:0.8rem;'>Zurich {jetzt}</p>",
#                 unsafe_allow_html=True)

# uhr()

# df = f.daten_laden()

# st.title("Interactive Analysis")

# # Auswahl: einmal wählen, dann auf den Knopf drücken
# with st.form("auswahl"):
#     kanton = st.selectbox("Canton with minimum wage", [
#                           "Neuenburg", "Genf", "Basel-Stadt"])

#     alle_kontrollen = sorted(df["Canton"].unique())
#     for k in ["Neuenburg", "Genf", "Basel-Stadt"]:
#         alle_kontrollen.remove(k)
#     kontrollen = st.multiselect("Control cantons", alle_kontrollen)

#     knopf = st.form_submit_button("Compare")

# # Erst weitermachen, wenn der Knopf gedrückt wurde
# if not knopf:
#     st.stop()

# # Keine Kontrollen gewählt: Standard aus funktionen.py nehmen
# if kontrollen == []:
#     kontrollen = f.KONTROLLEN[kanton]

# st.write("Kontrollen:", ", ".join(kontrollen))

# st.header("Parallel Trends")
# st.pyplot(f.grafik_trends(df, kanton, kontrollen))

# st.header("Event Study")
# st.pyplot(f.grafik_event_study(df, kanton, kontrollen))

# st.header("Difference in Differences")
# st.pyplot(f.grafik_did(df, kanton, kontrollen))
# st.dataframe(f.did_tabelle(df, kanton, kontrollen), hide_index=True)
# st.caption("* p < 0.1   ** p < 0.05   *** p < 0.01")


## Code von Caner
# SEITE 2: Interaktiv (Caner)
# Die Person wählt selbst einen Mindestlohn-Kanton und Kontrollkantone.
# Danach werden DiD und Event Study für diese Auswahl berechnet.

import streamlit as st
import funktionen as f

st.set_page_config(page_title="Interactive", layout="wide")

df = f.daten_laden()
# Grafik zentriert anzeigen: mittlere Spalte = 4/6 der Seitenbreite
def zeige_grafik(fig):
    links, mitte, rechts = st.columns([1, 4, 1])
    mitte.pyplot(fig)

st.title("Try it yourself")
st.write("Choose a canton with a minimum wage and one or more control cantons. "
         "The analyses below are calculated directly from the data for your selection.")


# ------------------------------------------------------------
# 1. Auswahl
# ------------------------------------------------------------
st.header("1. Your selection")



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
    border-color: #eb6834 !important;
}
.st-key-kanton button[data-selected="true"] *,
.st-key-kontrollen button[data-selected="true"] * {
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

# Mindestlohn-Kanton (nur die drei aus unserer Analyse), genau einer wählbar
kanton = st.pills(
    "Canton with minimum wage",
    options=list(f.EINFUEHRUNG),
    selection_mode="single",
    default="Neuenburg",
    key="kanton",
)

# Kontrollkantone: alle Kantone ohne Mindestlohn, mehrere wählbar
moegliche_kontrollen = sorted(k for k in df["Canton"].unique() if k not in f.EINFUEHRUNG)

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
st.header("2. Parallel Trends")

zeige_grafik(f.grafik_trends(df, kanton, kontrollen)) #Zeige_grafik zentriert einfach grafik, nur f.grafik_trend => nicht zentriert

# ------------------------------------------------------------
# 3. Difference-in-Differences
# ------------------------------------------------------------
st.header("3. Difference-in-Differences")

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
st.header("4. Event Study")

zeige_grafik(f.grafik_event_study(df, kanton, kontrollen))