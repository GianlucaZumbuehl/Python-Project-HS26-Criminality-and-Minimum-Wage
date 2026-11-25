# STARTSEITE: Navigation (Caner)
# Starten im Terminal:
#   cd streamlit_app
#   streamlit run Home.py

import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

# ------------------------------------------------------------
# Uhr oben rechts
# ------------------------------------------------------------


@st.fragment(run_every=10)
def uhr():
    jetzt = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%H:%M")
    st.markdown(f"<p style='text-align:right; font-size: 1.5rem;'>{jetzt}</p>",
                unsafe_allow_html=True)


uhr()


st.set_page_config(page_title="Home", layout="wide")

st.title("Minimum Wage and Crime in Swiss Cantons", anchor=False) #, anchor=False makes the weird symbol next to the title disappear
st.write("Annette Pitch")

st.header("What you find in this app", anchor=False)



st.subheader("Analysis", anchor=False)
st.write("To answer our main question regarding the effect of minimum wage on shoplifting we analysed the rate of persons aged 20-29 accused of shoplifting in various Swiss cantons (BFS police crime statistics, 2010-2025). The parallel trend graphs were used to check whether the cantons developed similarly before the minimum wage was introduced. The difference-in-differences (DiD) regression estimates the effect and the event study shows how the differences evolve year by year. Regarding our regression, the minimum wage reduced the rate of 20–29-year-olds accused of shoplifting by 41.2% in Neuenburg (highly statistically significant, p-value 0.0001) and by 44.1% in Basel-Stadt (highly statistically significant p-value = 0.00004) compared to the other control cantons. In Genf the effect is not statistically significant. Overall, our results suggest that a minimum wage may reduce shoplifting among young adults. ")
    

st.subheader("Interactive", anchor=False)
st.write("Here you can choose a canton with a minimum wage and your own control cantons and check for parallel trends and the analysis yourself.  Not all cantons are available due to missing data. ")
   