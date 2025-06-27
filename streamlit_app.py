import streamlit as st
import pandas as pd
import altair as alt

df = pd.read_csv("Massachusetts Food Access Data - Sheet1.csv")
st.set_page_config(layout="wide")
st.title("🥗✅ Mapping Food Access in Massachusetts")

df["County"] = df["County"].str.replace(" County", "", regex=False)
df["Pct_Households_No_Vehicle"] = (df["TractHUNV"] / df["OHU2010"]) * 100
df["LowAccessPopulation"] = df["LALOWI05_10"].fillna(0)

# Top 10 tracts by food inaccessibility
top10 = df.nlargest(10, "LowAccessPopulation")[["CensusTract", "County", "LowAccessPopulation"]]


# Overview/Intro
st.subheader("📝 **Overview**")
with st.expander("📝 Understanding Food Access"):
    st.markdown("""
Food access refers to the ability of ​​individuals and communities to obtain affordable, 
nutritious food –  shaped by physical proximity, economic affordability, and social 
accessibility. It is fundamentally linked to public health, economic stability, and social equity.

When access is limited, individuals may face food insecurity: limited or uncertain availability 
of adequate food, often due to lack of money or resources. This is common in food deserts (areas 
with limited access to grocery stores) and food swamps (areas with many fast food and convenience stores).

Despite being one of the wealthiest states, Massachusetts faces serious food access challenges 
across its diverse communities. Urban areas often lack grocery stores in low-income neighborhoods, 
while rural areas struggle with transportation barriers.

This dashboard focuses on Massachusetts to show that food insecurity can persist even in states 
with strong safety nets. These patterns highlight how economic inequality, geography, and systemic 
issues shape food access – offering insights that apply across the U.S.
        """)


# Definiitons
# Add definitions expander
with st.expander("📚 Key Definitions"):
    st.markdown("""
- **Census Tracts**: Small, relatively permanent geographic subdivisions of a county designed for statistical purposes by the U.S. Census Bureau.
- **LILA (Low-Income, Low-Access) Tracts**: Census tracts where a significant share of the population is both low-income and lives far from the nearest grocery store.
- **Urban Tracts**: Tracts designated as part of an urban area, generally meaning they are densely populated and developed compared to rural areas.
    """)

# Tips for using sidebar
with st.expander("📝 Tips!"):
    st.markdown("""
### 📈 Charts
- When **County** is selected as **All**, you can hover over the point/bar on the chart/plot.
- You can hover over the charts to see additional information about the county on all the charts!
- On the **Median Family Income vs Poverty Rate** scatterplot, you can interact with it by zooming and brushing.  

### 🔍 Sidebar
- The **County** filter is to help explore the county you are interested in! 
- The **Compare with Other Counties** can be used to select other counties you want to compare the initial county you chose in **County**. You can choose more than one!
- By selecting the check box **Urban Tracts Only** you can see the census tracts that fall within an urban area. 
- By dragging the **Median Income Range** bar, you can choose your desired income range you want to explore. 
    """)


total_tracts = len(df)
percent_LILA = (df["LILATracts_1And10"].sum() / total_tracts) * 100
avg_poverty = df["PovertyRate"].mean()
avg_income = df["MedianFamilyIncome"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Census Tracts", f"{total_tracts}")
col2.metric("% LILA Tracts", f"{percent_LILA:.1f}%")
col3.metric("Average Poverty Rate", f"{avg_poverty:.1f}%")
col4.metric("Average Median Family Income", f"${avg_income:,.0f}")

st.markdown("---")

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


# Shared selection - used in both charts
selection = alt.selection_point(
    fields= ["County"],
    bind='legend',
    on="mouseover"
)


# Chart 1: Scatter Plot with Brushing
st.subheader("📊 Relationships Between Income, Poverty & Vehicle Access")
brush = alt.selection_interval()

scatter = alt.Chart(filtered).mark_circle(opacity=0.7).encode(
    x=alt.X("MedianFamilyIncome:Q", title="Median Family Income"),
    y=alt.Y("PovertyRate:Q", title="Poverty Rate (%)"),
    size=alt.Size("Pop2010:Q", title="Population", scale=alt.Scale(range=[0, 100])),
    color=alt.condition(
        selection,
        "County:N",
        alt.value('lightgray'),
        title="County",
        scale=alt.Scale(scheme='category20')
    ),
    tooltip=[
    alt.Tooltip("CensusTract:N", title="Census Tract"),
    alt.Tooltip("County:N", title="County"),
    alt.Tooltip("Pop2010:Q", title="Population", format=",.0f"),
    alt.Tooltip("PovertyRate:Q", title="Poverty Rate (%)", format=".2f"),
    alt.Tooltip("MedianFamilyIncome:Q", title="Median Family Income", format="$.2f")
]
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
    color=alt.condition(
        selection,
        'County:N',
        alt.value('lightgray'),
        title='County',
        scale=alt.Scale(scheme='category20')
    ),
    tooltip=[
    alt.Tooltip("mean(Pct_Households_No_Vehicle):Q", title="% Without Vehicle", format=".2f")
]
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
    color=alt.condition(
        selection,
        'County:N',
        alt.value('lightgray'),
        title="County",
        scale=alt.Scale(scheme='category20')
    ),
    tooltip=[
        alt.Tooltip("mean(Pct_Households_No_Vehicle):Q", title="% Without Vehicle", format=".2f")
    ]
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

st.markdown("---")

# Chart 3: Top 10 Food Inaccessible Tracts 
st.subheader("🏙️ Top 10 Tracts with Highest Low-Access Population")
st.write("Hover over each bar in the graph to view exact numbers of the low access population in each county and to see which county!")
bar_top10 = alt.Chart(top10).mark_bar().encode(
    x=alt.X("CensusTract:N", sort="-x", title="Census Tract", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("LowAccessPopulation:Q", title="Low-Access Population"),
    tooltip=[
    alt.Tooltip("County:N", title="County"),
    alt.Tooltip("LowAccessPopulation:Q", title="Low-Access Population", format=",.2f")
]
).properties(
    width=700,
    height=400,
    title="Top 10 Tracts with Highest Food Inaccessibility"
)

st.altair_chart(bar_top10, use_container_width=True)

st.markdown("---")

# CHART 4: Choropleth Map of MA
import plotly.express as px
import requests

# Aggregate county-level statistics
county_summary = df.groupby("County").agg({
    "LILATracts_1And10": "sum",
    "CensusTract": "count",
    "Pct_Households_No_Vehicle": "mean",
    "MedianFamilyIncome": "mean",
    "PovertyRate": "mean"
}).reset_index()

# Calculate % LILA Tracts
county_summary["% LILA Tracts"] = (
    county_summary["LILATracts_1And10"] / county_summary["CensusTract"]
) * 100

# Round numeric values to 2 decimal places
county_summary["MedianFamilyIncome"] = county_summary["MedianFamilyIncome"].round(2)
county_summary["PovertyRate"] = county_summary["PovertyRate"].round(2)
county_summary["Pct_Households_No_Vehicle"] = county_summary["Pct_Households_No_Vehicle"].round(2)
county_summary["% LILA Tracts"] = county_summary["% LILA Tracts"].round(2)

# Rename columns for cleaner tooltips
county_summary.rename(columns={
    "MedianFamilyIncome": "Median Family Income ($)",
    "PovertyRate": "Poverty Rate (%)",
    "Pct_Households_No_Vehicle": "% Without Vehicle",
}, inplace=True)

# Add FIPS codes
county_fips = {
    "Barnstable County": "25001", "Berkshire County": "25003", "Bristol County": "25005",
    "Dukes County": "25007", "Essex County": "25009", "Franklin County": "25011",
    "Hampden County": "25013", "Hampshire County": "25015", "Middlesex County": "25017",
    "Nantucket County": "25019", "Norfolk County": "25021", "Plymouth County": "25023",
    "Suffolk County": "25025", "Worcester County": "25027"
}
county_summary["fips"] = county_summary["County"].map(county_fips)

# Load US counties geojson
geo_url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
geo_json = requests.get(geo_url).json()

# Merge geo info with summary
all_fips = [feature["id"] for feature in geo_json["features"]]
all_counties_df = pd.DataFrame({"fips": all_fips})
choropleth_df = all_counties_df.merge(county_summary, on="fips", how="left")

# Create the choropleth map
fig = px.choropleth(
    choropleth_df,
    geojson=geo_json,
    locations="fips",
    color="% LILA Tracts",
    color_continuous_scale="Reds",
    range_color=(0, county_summary["% LILA Tracts"].max()),
    labels={
        "% LILA Tracts": "% LILA Tracts",
        "Median Family Income ($)": "Median Family Income ($)",
        "Poverty Rate (%)": "Poverty Rate (%)",
        "% Without Vehicle": "% Without Vehicle"
    },
    hover_data={
        "County": True,
        "Median Family Income ($)": True,
        "Poverty Rate (%)": True,
        "% Without Vehicle": True,
        "fips": False
    },
    title="Percentage of Low-Income Low-Access (LILA) Tracts by County"
)

# Configure map appearance
fig.update_geos(
    visible=False,
    fitbounds="locations",
    projection_scale=3.5,
    center={"lat": 42.8, "lon": -73.0}
)

st.subheader("🗺️ Food Access Map")
st.write("Hover over each county to see which county it is, percentage of LILA Tracts, and more! You can also interact with the map by zooming in and out.")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Key Takeaways Section 
st.subheader("📌 Key Takeaways and Reflections")

tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Health Impacts", "Policy Recommendations", "Beyond MA + Action"])

with tab1:
    st.markdown("""
### 💡 Summary of Insights
- Tracts with **low median family income** and **high poverty rates** are often also classified as Low-Income and Low Access (LILA).
- Lack of **vehicle access** adds another layer of difficulty in accessing grocery stores, especially in these high-need communities.
- The **top 10 most food-inaccessible tracts** span multiple counties, revealing that this is not just an urban or rural issue — it's widespread.

This is a **statewide and national challenge** with real public health and equity implications.
    """)

with tab2:
    st.markdown("""
### 🩺 Health Implications
Food insecurity contributes to:
- **Higher rates of chronic disease** (e.g. diabetes, hypertension, cardiovascular disease, obesity) from reliance on processed, 
                high-calorie food options that provide sustenance bu lack essential nutrients.
- Poor **mental health outcomes**, increased rates of depression, anxiety, and stress-related disorders due to chronic stress over food insecurity.
- **Increased healthcare costs** and systemic strain as there would be an increase in emergency room visits, hospital readmissions, and long term 
                care needs, especially in underserved regions.
    """)

with tab3:
    st.markdown("""
### 🏛️ Policy & Equity Recommendations

**Actionable data like this dashboard** should inform equity-centered urban and rural planning.
- Incentivize **grocery store development** in underserved tracts.
- Fund **transportation programs** for low-income and vehicle-less communities.
- Scale up **SNAP/WIC access and outreach** in low-access regions.
- Remove **zoning barriers** to allow mobile and pop-up grocery markets.
- Encourage **cross-department collaboration** between health, transit, housing, and food agencies.
    """)

with tab4:
    st.markdown("""
### 🌎 Beyond Massachusetts + Call to Action

- While this dashboard focuses on Massachusetts, similar patterns exist nationwide.
-  A more just food system means confronting transportation, poverty, zoning laws, 
                and health disparities together.
- 📣 **What You Can Do**:
    - Vote and advocate for **policies that support food justice**.
    - Partner with or volunteer for **local mutual aid groups and food co-ops**.
    - Use and share tools like this dashboard to **inform others and drive action**.
    """)
