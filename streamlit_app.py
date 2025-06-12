import streamlit as st
import altair as alt
import pandas as pd

df = pd.read_csv("Massachusetts Food Access Data - Sheet1.csv")

st.set_page_config(layout="wide")
st.title("🥘 Food Access in Massachusetts")

st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

# visualization 1 (will attempt to switch)
chart1 = alt.Chart(df).mark_circle(opacity=0.7).encode(
    x=alt.X("MedianFamilyIncome",
            scale=alt.Scale(domain=[0, df["MedianFamilyIncome"].max() + 1000]),
            axis=alt.Axis(tickMinStep=1000, title="Median Family Income")),
    y=alt.Y("PovertyRate", title="Poverty Rate (%)"),
    size=alt.Size("Pop2010", title="Population", scale=alt.Scale(range=[0, 100])),
    color=alt.Color("County", title="County"),
    tooltip=["CensusTract", "County", "Urban", "Pop2010", "PovertyRate","MedianFamilyIncome"]
).properties(
    title="Median Family Income vs Poverty Rate",
    width=600,
    height=400
).interactive()

st.altair_chart(chart1, use_container_width=True)

