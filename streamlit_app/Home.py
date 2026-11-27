# EINSTIEG UND NAVIGATION (Caner)
# Starten im Terminal:
#   cd streamlit_app
#   streamlit run Home.py
#
# Hier wird nur festgelegt, welche Seiten es gibt.
# Die Navigation erscheint oben. Der Inhalt der Startseite liegt in pages/0_Startseite.py.

import streamlit as st

st.set_page_config(layout="wide")

seiten = st.navigation([
    st.Page("pages/0_Startseite.py", title="Home", default=True),
    st.Page("pages/1_Analysis.py", title="Analysis"),
    st.Page("pages/2_Interactive.py", title="Interactive"),
], position="top")

seiten.run()
