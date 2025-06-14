import streamlit as st
import pandas as pd
import altair as alt

df = pd.read_csv("Massachusetts Food Access Data - Sheet1.csv")
st.set_page_config(layout="wide")
st.title("🥗✅ Mapping Food Access in Massachusetts")

df["Pct_Households_No_Vehicle"] = (df["TractHUNV"] / df["OHU2010"]) * 100
df["LowAccessPopulation"] = df["LALOWI05_10"].fillna(0)

# Top 10 tracts by food inaccessibility
top10 = df.nlargest(10, "LowAccessPopulation")[["CensusTract", "County", "LowAccessPopulation"]]


# Overview/Intro
st.subheader("📝 **Overview: Understanding Food Access**")
with st.expander("📝 Overview: Understanding Food Access"):
    st.markdown("""
Food access refers to the ability of individuals and communities to obtain affordable and
nutricious food that meets needs through physical proximity to food sources, economic affordability,
and social accessibility. Food access is fundamentally linked to public health, economic stability, 
and social inequity.

When people lack adequate food access, they may experience food insecurity: the condition of having limited 
or uncertain availability of nutritionally adequate foods, due to the lack of money and other resources. People who 
experience food insecurity often live in food deserts (areas with limited access to grocery stores) or food swamps 
(areas with many fast food and convenient stores).
                
Despite being one of the wealthiest states in the nation, Massachusetts faces significant food access 
challenges across it's diverse communities. Urban areas struggle with food deserts and limited grocery store access 
and have concentrated low income populations with poor food acess. Rural areas present transportation barriers for 
people who travel long distances to grocery stores.
                
The following data visualizations focus on Massachusetts to demonstrate that food access limitations and 
food insecurity persist even in wealthy states with strong social safety nets. By examining Massachusetts, we can see 
how economic inequality, geographic barriers, and systemic challenges create food access desparities. The patterns 
relationships, and insights revealed through the data on Massachusetts can be applied to understand food access 
challenges in other states across the country, providing a framework for analyzing how local factors interact 
with broader socioeconomic forces to shape food security outcomes.
        """)

total_tracts = len(df)
percent_LILA = (df["LILATracts_1And10"].sum() / total_tracts) * 100
avg_poverty = df["PovertyRate"].mean()
avg_income = df["MedianFamilyIncome"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Census Tracts", f"{total_tracts}")
col2.metric("% LILA Tracts", f"{percent_LILA:.1f}%")
col3.metric("Avg Poverty Rate", f"{avg_poverty:.1f}%")
col4.metric("Avg Median Family Income", f"${avg_income:,.0f}")

# Sidebar Filters
st.sidebar.header("🔎 Filters")
counties = ["All"] + sorted(df["County"].dropna().unique())
selected_county = st.sidebar.selectbox("County", counties)

counties_multi= sorted(df["County"].dropna().unique())
selected_counties= st.sidebar.multiselect("Compare with Other Counties", counties_multi)

urban_only = st.sidebar.checkbox("Urban Tracts Only", value=False)
income_min = int(df["MedianFamilyIncome"].min())
income_max = int(df["MedianFamilyIncome"].max())
income_range = st.sidebar.slider("Median Income Range", min_value=income_min,
                                 max_value=income_max, value=(income_min, income_max))

filtered = df.copy()
if selected_county != "All" and selected_counties:
    all_counties = [selected_county] + selected_counties
    filtered = filtered[filtered["County"].isin(all_counties)]
elif selected_county != "All":
    filtered = filtered[filtered["County"] == selected_county]
elif selected_counties:
    filtered = filtered[filtered["County"].isin(selected_counties)]
if urban_only: filtered = filtered[filtered["Urban"] == 1]
filtered = filtered[(filtered["MedianFamilyIncome"] >= income_range[0]) &
                    (filtered["MedianFamilyIncome"] <= income_range[1])]


#shared selection
selection = alt.selection_point(
    fields= ["County"],
    bind='legend',
    on = "mouseover"
)

# Chart 1: Scatter Plot with Brushing
st.subheader("📊 Relationships Between Income, Poverty & Vehicle Access")
brush = alt.selection_interval()

st.subheader("📝 **Tips and Notes for Coordinated Visualizations**")
with st.expander("📝 Tips!"):
    st.markdown(""" 

                """)
scatter = alt.Chart(filtered).mark_circle(opacity=0.7).encode(
    x=alt.X("MedianFamilyIncome:Q", title="Median Family Income"),
    y=alt.Y("PovertyRate:Q", title="Poverty Rate (%)"),
    size=alt.Size("Pop2010:Q", title="Population", scale=alt.Scale(range=[0, 100])),
    color=alt.Color("County:N", title="County", scale=alt.Scale(scheme='category20')),
    tooltip=["CensusTract", "County", "Pop2010", "PovertyRate", "MedianFamilyIncome"]
).add_selection(
    brush
).properties(
    title="Median Family Income vs Poverty Rate",
    width=600,
    height=430
).add_params(
    selection
).interactive()

# Chart 2A: Brushed Bar Chart (linked to scatter)
bar_brushed = alt.Chart(filtered).transform_filter(
    brush
).mark_bar().encode(
    x=alt.X("mean(Pct_Households_No_Vehicle):Q", title="% Without Vehicle", scale=alt.Scale(domain=[0, 40])),
    y=alt.Y("County:N", sort="-x", title="County"),
    color=alt.Color("County:N", title="County", scale=alt.Scale(scheme='category20')),
    tooltip=["mean(Pct_Households_No_Vehicle):Q"],
).properties(
    title="Percentage of Households Without Vehicles",
    width=600,
    height=430
).add_params(
    selection
)

# Chart 2B: Full fallback bar chart (unlinked)
bar_fallback = alt.Chart(filtered).mark_bar().encode(
    x=alt.X("mean(Pct_Households_No_Vehicle):Q", title="% Without Vehicle", scale=alt.Scale(domain=[0, 40])),
    y=alt.Y("County:N", sort="-x", title="County"),
    color=alt.Color("County:N", title="County", scale=alt.Scale(scheme='category20')),
    tooltip=["mean(Pct_Households_No_Vehicle):Q"],
).properties(
    title="Percentage of Households Without Vehicles",
    width=600,
    height=430
).add_params(
    selection
)

# Layout: Put Chart 1 and Chart 2 fallback together
col1, col2 = st.columns(2)
with col1:
    st.altair_chart(scatter, use_container_width=True)
with col2:
    st.altair_chart(bar_fallback, use_container_width=True)

# Chart 3: Top 10 Food Inaccessible Tracts 
st.subheader("🏙️ Top 10 Tracts with Highest Low-Access Population")

bar_top10 = alt.Chart(top10).mark_bar().encode(
    x=alt.X("CensusTract:N", sort="-x", title="Census Tract"),
    y=alt.Y("LowAccessPopulation:Q", title="Low-Access Population"),
    tooltip=["County", "LowAccessPopulation"]
).properties(
    width=700,
    height=400,
    title="Top 10 Tracts with Highest Food Inaccessibility"
)

st.altair_chart(bar_top10, use_container_width=True)

# CHART 4: Choropleth Map of MA 
import plotly.express as px
import requests

county_summary = df.groupby("County").agg({
    "LILATracts_1And10": "sum",
    "CensusTract": "count",
    "Pct_Households_No_Vehicle": "mean",
    "MedianFamilyIncome": "mean",
    "PovertyRate": "mean"
}).reset_index()

county_summary["% LILA Tracts"] = (
    county_summary["LILATracts_1And10"] / county_summary["CensusTract"]
) * 100

county_fips = {
    "Barnstable County": "25001", "Berkshire County": "25003", "Bristol County": "25005",
    "Dukes County": "25007", "Essex County": "25009", "Franklin County": "25011",
    "Hampden County": "25013", "Hampshire County": "25015", "Middlesex County": "25017",
    "Nantucket County": "25019", "Norfolk County": "25021", "Plymouth County": "25023",
    "Suffolk County": "25025", "Worcester County": "25027"
}
county_summary["fips"] = county_summary["County"].map(county_fips)

geo_url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
geo_json = requests.get(geo_url).json()

all_fips = [feature["id"] for feature in geo_json["features"]]
all_counties_df = pd.DataFrame({"fips": all_fips})
choropleth_df = all_counties_df.merge(county_summary, on="fips", how="left")

fig = px.choropleth(
    choropleth_df,
    geojson=geo_json,
    locations="fips",
    color="% LILA Tracts",
    color_continuous_scale="Reds",
    range_color=(0, county_summary["% LILA Tracts"].max()),
    labels={"% LILA Tracts": "% LILA Tracts"},
    hover_data={
        "County": True,
        "MedianFamilyIncome": True,
        "PovertyRate": True,
        "Pct_Households_No_Vehicle": True,
        "fips": False
    },
    title="Percentage of Low-Income Low-Access (LILA) Tracts by County"
)

fig.update_geos(
    visible=False,
    fitbounds="locations",
    projection_scale=3.5,  # Zoom out more to show MA + neighbors
    center={"lat": 42.8, "lon": -73.0}  # Center over MA/NY border
)

st.subheader("🗺️ Food Access Map")
st.plotly_chart(fig, use_container_width=True)

# Key Takeaways Section 
st.subheader("📌 Key Takeaways and Reflections")
with st.expander("📌 Key Takeaways and Reflections"):
    st.markdown("""
### 💡 Summary of Insights
- Tracts with **low median family income** and **high poverty rates** are often also classified as **Low-Income and Low Access (LILA)**.
- Lack of **vehicle access** adds another layer of difficulty in accessing grocery stores, especially in these high-need communities.
- The **top 10 most food-inaccessible tracts** span multiple counties, revealing that this is not just an urban or rural issue — it's widespread.

### 🩺 Health Implications
Food insecurity contributes to:
- Higher rates of **chronic disease** (e.g. diabetes, hypertension, cardiovascular disease, obesity) due to reliance on processed, calorie dense foods
                that provide sustenance but lack essential nutrients.
- Poor **mental health outcomes** increased rates of depression, anxiety, and stress related disorders from the chronic stress of not knowing when the 
                next meal will come.
- Increased healthcare costs and systemic strain as there would be an increase in emergency room visits, hospital readmissions, and
                long term care needs.

### 🏛️ Policy & Equity Considerations
- Data like this should inform **grocery store placements**, **transportation subsidies**, and **SNAP/WIC outreach**.
- Equity-focused infrastructure investment can reduce access gaps.

### 🌎 Beyond Massachusetts
While this dashboard focuses on Massachusetts, similar patterns exist nationwide.  
A more just food system means confronting **transportation**, **poverty**, **zoning laws**, and **health disparities** together. 
    """)
