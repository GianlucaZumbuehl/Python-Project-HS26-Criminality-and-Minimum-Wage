# SEITE 1: Resultate und Diskussion
# Starten im Terminal:
#   cd streamlit_app
#   streamlit run app.py

import streamlit as st
import funktionen as f

st.set_page_config(page_title="Results", layout="wide")
df = f.daten_laden()

st.title("Minimum Wage and Crime in Swiss Cantons")
st.write("PLATZHALTER: Kurze Einleitung zur Fragestellung.")


# ------------------------------------------------------------
# 1. Parallel Trends
# ------------------------------------------------------------
st.header("1. Parallel Trends")
st.write("PLATZHALTER: Welche Kontrollkantone haben die stärksten parallelen Trends?")

tab1, tab2, tab3 = st.tabs(["Neuenburg", "Genf", "Basel-Stadt"])
with tab1:
    st.pyplot(f.grafik_trends(df, "Neuenburg", f.KONTROLLEN["Neuenburg"]))
with tab2:
    st.pyplot(f.grafik_trends(df, "Genf", f.KONTROLLEN["Genf"]))
with tab3:
    st.pyplot(f.grafik_trends(df, "Basel-Stadt", f.KONTROLLEN["Basel-Stadt"]))


# ------------------------------------------------------------
# 2. Regressionen und Event Study
# ------------------------------------------------------------
st.header("2. Regressions and Event Study")
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
# 3. Diskussion
# ------------------------------------------------------------
st.header("3. Discussion and Conclusion")

st.subheader("How we found our results")
st.write("PLATZHALTER: Vorgehen und warum wir es so gemacht haben.")

st.subheader("Data cleaning")
st.write("PLATZHALTER: Wie wir die Daten bereinigt haben.")

st.subheader("Significance")
st.write("PLATZHALTER: Diskussion der Signifikanz.")

st.subheader("Conclusion")
st.write("PLATZHALTER: Fazit.")
