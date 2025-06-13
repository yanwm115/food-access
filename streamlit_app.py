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
st.write("Food access refers to the ability of individuals and communities to obtain affordable and " \
"nutricious food that meets needs through physical proximity to food sources, economic affordability," \
"and social accessibility. Food access is fundamentally linked to public health, economic stability, "
"and social inequity.")
st.write("When people lack adequate food access, they may experience food insecurity: the condition of having limited "
"or uncertain availability of nutritionally adequate foods, due to the lack of money and other resources. People who " \
"experience food insecurity often live in food deserts (areas with limited access to grocery stores) or food swamps " \
"(areas with many fast food and convenient stores).")
st.write("Despite being one of the wealthiest states in the nation, Massachusetts faces significant food access" \
"challenges across it's diverse communities. Urban areas struggle with food deserts and limited grocery store access " \
"and have concentrated low income populations with poor food acess. Rural areas present transportation barriers for " \
"people who travel long distances to grocery stores.")
st.write("The following data visualizations focus on Massachusetts to demonstrate that food access limitations and "
"food insecurity persist even in wealthy states with strong social safety nets. By examining Massachusetts, we can see "
"how economic inequality, geographic barriers, and systemic challenges create food access desparities. The patterns "
"relationships, and insights revealed through the data on Massachusetts can be applied to understand food access "
"challenges in other states across the country, providing a framework for analyzing how local factors interact "
"with broader socioeconomic forces to shape food security outcomes.")

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

# Chart 1: Scatter Plot with Brushing
st.subheader("📊 Coordinated Visualizations")
brush = alt.selection_interval()

scatter = alt.Chart(filtered).mark_circle(opacity=0.7).encode(
    x=alt.X("MedianFamilyIncome:Q", title="Median Family Income"),
    y=alt.Y("PovertyRate:Q", title="Poverty Rate (%)"),
    size=alt.Size("Pop2010:Q", title="Population", scale=alt.Scale(range=[0, 100])),
    color=alt.Color("County:N", title="County", scale=alt.Scale(scheme='category20')),
    tooltip=["CensusTract", "County", "Pop2010", "PovertyRate", "MedianFamilyIncome"]
).add_selection(
    brush
).properties(
    title="Chart 1: Median Family Income vs Poverty Rate",
    width=600,
    height=400
)

# Chart 2A: Brushed Bar Chart (linked to scatter)
bar_brushed = alt.Chart(filtered).transform_filter(
    brush
).mark_bar().encode(
    x=alt.X("mean(Pct_Households_No_Vehicle):Q", title="% Without Vehicle"),
    y=alt.Y("County:N", sort="-x", title="County"),
    color=alt.Color("County:N", title="County", scale=alt.Scale(scheme='category20')),
    tooltip=["mean(Pct_Households_No_Vehicle):Q"],
).properties(
    title="Chart 2: % Without Vehicles (From Brushed Scatter Selection)",
    width=600,
    height=400
)

# Chart 2B: Full fallback bar chart (unlinked)
bar_fallback = alt.Chart(filtered).mark_bar().encode(
    x=alt.X("mean(Pct_Households_No_Vehicle):Q", title="% Without Vehicle"),
    y=alt.Y("County:N", sort="-x", title="County"),
    color=alt.Color("County:N", title="County", scale=alt.Scale(scheme='category20')),
    tooltip=["mean(Pct_Households_No_Vehicle):Q"],
).properties(
    title="Chart 2: % Without Vehicles (All Filtered Tracts)",
    width=600,
    height=400
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


# CHART 4: GEO MAP - made up coordinates as placeholders
import numpy as np
import pydeck as pdk

# Simulate lat/lon for visualization (for demo purposes only)
# Replace this with actual coordinates per tract if available
np.random.seed(42)
filtered_map = filtered.copy()
county_latlon = {
    "Barnstable County": (41.7, -70.3),
    "Bristol County": (41.8, -71.1),
    "Essex County": (42.6, -70.9),
    "Hampden County": (42.1, -72.6),
    "Hampshire County": (42.4, -72.6),
    "Middlesex County": (42.5, -71.3),
    "Norfolk County": (42.2, -71.2),
    "Plymouth County": (42.0, -70.8),
    "Suffolk County": (42.35, -71.07),
    "Worcester County": (42.3, -71.8),
}

filtered_map["lat"] = filtered_map["County"].apply(lambda x: county_latlon.get(x, (42.3, -71.1))[0] + np.random.uniform(-0.05, 0.05))
filtered_map["lon"] = filtered_map["County"].apply(lambda x: county_latlon.get(x, (42.3, -71.1))[1] + np.random.uniform(-0.05, 0.05))

# Define color by category
filtered_map["color"] = filtered_map["LILATracts_1And10"].apply(lambda x: [255, 0, 0] if x == 1 else [0, 120, 255])

st.subheader("🗺️ Geo Map of Low-Income / Low-Access Tracts")

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=42.3,
        longitude=-71.1,
        zoom=7,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=filtered_map,
            get_position='[lon, lat]',
            get_fill_color='color',
            get_radius=500,
            pickable=True,
            auto_highlight=True,
        )
    ],
    tooltip={"text": "Tract: {CensusTract}\nCounty: {County}\nIncome: ${MedianFamilyIncome}\nNo Vehicle: {Pct_Households_No_Vehicle:.1f}%"}
))

# Key Takeaways Section 
with st.expander("📌 Key Takeaways and Reflections"):
    st.markdown("""
### 💡 Summary of Insights
- Tracts with **low median family income** and **high poverty rates** are often also classified as **Low-Income and Low Access (LILA)**.
- Lack of **vehicle access** adds another layer of difficulty in accessing grocery stores, especially in these high-need communities.
- The **top 10 most food-inaccessible tracts** span multiple counties, revealing that this is not just an urban or rural issue — it's widespread.

### 🩺 Health Implications
Food insecurity contributes to:
- Higher rates of **chronic disease** (e.g. diabetes, obesity)
- Poor **mental health outcomes**
- Increased healthcare costs and systemic strain

### 🏛️ Policy & Equity Considerations
- Data like this should inform **grocery store placements**, **transportation subsidies**, and **SNAP/WIC outreach**.
- Equity-focused infrastructure investment can reduce access gaps.

### 🌎 Beyond Massachusetts
While this dashboard focuses on Massachusetts, similar patterns exist nationwide.  
A more just food system means confronting **transportation**, **poverty**, **zoning laws**, and **health disparities** together.
    """)

