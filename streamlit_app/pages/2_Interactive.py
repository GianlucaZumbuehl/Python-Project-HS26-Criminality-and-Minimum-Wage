# SEITE 2: Interaktiv
# Streamlit zeigt jede Datei im Ordner "pages" automatisch als eigene Seite an.

import streamlit as st
import funktionen as f

st.set_page_config(page_title="Interactive", layout="wide")
df = f.daten_laden()

st.title("Interactive Analysis")

# Auswahl: einmal wählen, dann auf den Knopf drücken
with st.form("auswahl"):
    kanton = st.selectbox("Canton with minimum wage", ["Neuenburg", "Genf", "Basel-Stadt"])

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
