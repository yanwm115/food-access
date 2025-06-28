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

st.subheader("📝 Understanding Food Access")

intro_tab, defs_tab, tips_tab = st.tabs(["📄 Overview", "📚 Definitions", "💡 Tips"])

with intro_tab:
    st.markdown("""
Food access refers to the ability of ​​individuals and communities to obtain affordable, 
nutritious food – shaped by physical proximity, economic affordability, and social 
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

with defs_tab:
    st.markdown("""
- **Census Tracts**: Small geographic areas within a county, used by the U.S. Census Bureau to collect and analyze population data.  
- **LILA Tracts**: Low-Income & Low-Access
    - Areas where a large portion of residents have low incomes and live far from supermarkets or large grocery stores. 
                These tracts face compounded challenges in both affordability and physical access to food.  
- **Urban Tracts**: Tracts designated as part of an urban area, generally meaning they are densely populated and developed compared to rural areas.  
""")
    
with tips_tab:
    st.markdown("""
<div style='font-size:18px; font-weight:600;'>📈 Using the Charts</div>
<ul style='margin-top: 4px;'>
  <li>When <strong>"All"</strong> is selected in the <strong>County</strong> dropdown, all counties will appear in the charts.</li>
  <li>Hover over any scatterplot point, bar, or map area for detailed information.</li>
  <li>You can zoom and pan on interactive charts when noted.</li>
</ul>

<div style='font-size:18px; font-weight:600;'>🔍 Exploring with the Sidebar</div>
<p style='margin: 4px 0;'>Each filter is labeled with which visualization it affects:</p>
<ul style='margin-top: 4px;'>
  <li><strong>County</strong>: Focuses the entire dashboard on one county.</li>
  <li><strong>Compare with Other Counties</strong>: Adds other counties for side-by-side comparison.</li>
  <li><strong>Urban Tracts Only</strong>: Limits the view to only tracts designated as urban.</li>
  <li><strong>Median Income Range</strong>: Filters census tracts within your selected income range.</li>
</ul>

<div style='font-size:18px; font-weight:600;'>🧭 Look Below for Insights</div>
<ul style='margin-top: 4px;'>
  <li>Colored context boxes below each chart provide guidance and takeaways based on your selections.</li>
</ul>
""", unsafe_allow_html=True)

st.markdown("### ")

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

# Shared selection - responds to both point hover and legend clicks
selection = alt.selection_point(
    fields=["County"],
    bind='legend',
    on="mouseover"
)

# Chart 1: Scatter Plot
st.subheader("📊 Relationships Between Income, Poverty & Vehicle Access")
st.write("🔍 Sidebar: Select County, Compare with Other Counties, Urban Tracts Only, and Median Income Range to explore.")
st.write("📈 Chart: Zoom in and out of the scatterplot. Hover over the scatter plot and bar graph to view more information. Click" \
" on the legend to see specific census tracts in each county.")

scatter = alt.Chart(filtered).mark_circle(opacity=0.7).encode(
    x=alt.X("MedianFamilyIncome:Q", title="Median Family Income"),
    y=alt.Y("PovertyRate:Q", title="Poverty Rate (%)"),
    size=alt.Size("Pop2010:Q", title="Population", scale=alt.Scale(range=[0, 120])),
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
).properties(
    title="Median Family Income vs Poverty Rate",
    width=600,
    height=430
).add_params(
    selection
).interactive()


# Chart 2A: Bar Chart (linked to scatter)
bar_chart = alt.Chart(filtered).mark_bar().encode(
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
    selection)

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
    selection)


# Layout: Put Chart 1 and Chart 2 fallback together
col1, col2 = st.columns(2)
with col1:
    st.altair_chart(scatter, use_container_width=True)
with col2:
    st.altair_chart(bar_fallback, use_container_width=True)


st.markdown(
    f"""
    <div style="background-color: #fffbe6; padding: 1rem; border-radius: 0.5rem; text-align: left; color: #665c00; font-size: 16px;">
        💡 Census tracts with <strong>lower median family incomes</strong> often experience <strong>higher poverty rates</strong>, creating a visible inverse trend. These areas also tend to have <strong>more households without vehicles</strong>, deepening access challenges to essential services like grocery stores.<br><br>
        Suffolk and Hampden counties stand out with the <strong>highest share of households lacking vehicles</strong> — a key factor in food access vulnerability.
    </div>""", unsafe_allow_html=True)

st.markdown("---")


# Chart 3: Food Inaccessible Tracts with Selection Options
st.subheader("🏙️ Food Inaccessible Tracts Analysis")
st.write("🔍 Sidebar: Select County to explore.")
st.write("📈 Chart: Select from selection box/drop down to view graphs. Hover each bar to view exact numbers of low access population and see which counties are in the top 10!")

# Create selection dropdown
view_option = st.selectbox(
    "Select view:",
    options=[
        "Top 10 Highest Low-Access Population",
        "Highest to Lowest by Low-Access Population", 
        "Lowest to Highest by Low-Access Population",
    ],
    index=0  # Default to first option
)

# Create shared color scale for consistency
county_color_scale = alt.Scale(scheme='category20')

# Function to create conditional opacity encoding based on selected county
def get_opacity_encoding(selected_county):
    # Always return full opacity - we'll only use stroke for highlighting
    return alt.value(1.0)

# Function to get stroke encoding based on selected county
def get_stroke_encoding(selected_county):
    if selected_county != "All":
        return alt.condition(
            alt.datum.County == selected_county,
            alt.value('black'),
            alt.value('transparent')
        )
    else:
        return alt.value('transparent')

# Function to get stroke width encoding based on selected county  
def get_stroke_width_encoding(selected_county):
    if selected_county != "All":
        return alt.condition(
            alt.datum.County == selected_county,
            alt.value(3),
            alt.value(0)
        )
    else:
        return alt.value(0)

# Prepare data and display chart based on selection
if view_option == "Top 10 Highest Low-Access Population":
    # Chart 1: Default - Top 10 with highlighting
    bar_chart = alt.Chart(top10).mark_bar().encode(
        x=alt.X("CensusTract:N", sort="-x", title="Census Tract", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("LowAccessPopulation:Q", title="Low-Access Population"),
        color=alt.Color("County:N", scale=county_color_scale, title="County"),
        opacity=get_opacity_encoding(selected_county),
        stroke=get_stroke_encoding(selected_county),
        strokeWidth=get_stroke_width_encoding(selected_county),
        tooltip=[
            alt.Tooltip("County:N", title="County"),
            alt.Tooltip("LowAccessPopulation:Q", title="Low-Access Population", format=",.2f")
        ]
    ).properties(
        width=700,
        height=400,
        title="Top 10 Tracts with Highest Food Inaccessibility"
    )
    st.write("Top 10 census tracts color-coded by county to show which counties have the highest low-access populations.")
    
elif view_option == "Highest to Lowest by Low-Access Population":
    # Chart 2: All tracts highest to lowest with highlighting
    bar_chart = alt.Chart(top10).mark_bar().encode(
        x=alt.X("CensusTract:N", sort="-y", title="Census Tract", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("LowAccessPopulation:Q", title="Low-Access Population"),
        color=alt.Color("County:N", scale=county_color_scale, title="County"),
        opacity=get_opacity_encoding(selected_county),
        stroke=get_stroke_encoding(selected_county),
        strokeWidth=get_stroke_width_encoding(selected_county),
        tooltip=[
            alt.Tooltip("County:N", title="County"),
            alt.Tooltip("LowAccessPopulation:Q", title="Low-Access Population", format=",.2f")
        ]
    ).properties(
        width=700,
        height=400,
        title="Top 10 Census Tracts Highest to Lowest by Low-Access Population"
    )
    st.write("Top 10 census tracts ranked from highest to lowest low-access population.")
    
else:
    bar_chart = alt.Chart(top10).mark_bar().encode(
        x=alt.X("CensusTract:N", sort="y", title="Census Tract", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("LowAccessPopulation:Q", title="Low-Access Population"),
        color=alt.Color("County:N", scale=county_color_scale, title="County"),
        opacity=get_opacity_encoding(selected_county),
        stroke=get_stroke_encoding(selected_county),
        strokeWidth=get_stroke_width_encoding(selected_county),
        tooltip=[
            alt.Tooltip("County:N", title="County"),
            alt.Tooltip("LowAccessPopulation:Q", title="Low-Access Population", format=",.2f")
        ]
    ).properties(
        width=700,
        height=400,
        title="Top 10 Census Tracts Lowest to Highest Low-Access Population"
    )
    st.write("Top 10 census tracts ranked from lowest to highest low-access population.")

st.altair_chart(bar_chart, use_container_width=True)

st.markdown(
    f"""
    <div style="background-color: #e6f3ff; padding: 1rem; border-radius: 0.5rem; text-align: left; color: #665c00; font-size: 16px;">
        💡 Here we took the top 10 census tracts with the highest food inaccessibility to see how low it is in Masachusetts.
        Census tracts with the highest food inaccessibility tend to be the areas we need to focus on the most. It can be seen that 
        a county in Hampshire has the highest low access population, followed by Essex, 
        another Hampshire county, and Worcester. <br>
    </div>""", unsafe_allow_html=True)


st.markdown("---")

# Chart 4: Map
import plotly.graph_objects as go
import requests

county_fips = {
    "Barnstable": "25001", "Berkshire": "25003", "Bristol": "25005", "Dukes": "25007",
    "Essex": "25009", "Franklin": "25011", "Hampden": "25013", "Hampshire": "25015",
    "Middlesex": "25017", "Nantucket": "25019", "Norfolk": "25021", "Plymouth": "25023",
    "Suffolk": "25025", "Worcester": "25027"}

county_summary = df.groupby("County", as_index=False).agg({
    "LILATracts_1And10": "sum",
    "CensusTract": "count",
    "Pct_Households_No_Vehicle": "mean",
    "MedianFamilyIncome": "mean",
    "PovertyRate": "mean"})

county_summary["% LILA Tracts"] = (
    county_summary["LILATracts_1And10"] / county_summary["CensusTract"]) * 100
county_summary = county_summary.round(2)
county_summary.rename(columns={
    "MedianFamilyIncome": "Median Family Income ($)",
    "PovertyRate": "Poverty Rate (%)",
    "Pct_Households_No_Vehicle": "% Without Vehicle",
}, inplace=True)
county_summary["fips"] = county_summary["County"].map(county_fips)

for island in ["Dukes", "Nantucket"]:
    if island not in county_summary["County"].values:
        county_summary = county_summary.append({
            "County": island,
            "LILATracts_1And10": 0,
            "CensusTract": 1,
            "% LILA Tracts": 0,
            "Median Family Income ($)": 0,
            "Poverty Rate (%)": 0,
            "% Without Vehicle": 0,
            "fips": county_fips[island]
        }, ignore_index=True)

geo_url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
geo_json = requests.get(geo_url).json()
geo_json["features"] = [f for f in geo_json["features"] if f["id"].startswith("25")]

choropleth = go.Choropleth(
    geojson=geo_json,
    locations=county_summary["fips"],
    z=county_summary["% LILA Tracts"],
    colorscale="Reds",
    zmin=0,
    zmax=county_summary["% LILA Tracts"].max(),
    marker_line_color="black",
    marker_line_width=0.5,
    featureidkey="id",
    colorbar_title="% LILA Tracts",
    text=county_summary.apply(
        lambda row: (
            f"County: {row['County']}<br>"
            f"% LILA Tracts: {row['% LILA Tracts']:.2f}<br>"
            f"Median Income: ${row['Median Family Income ($)']:,.0f}<br>"
            f"Poverty Rate (%): {row['Poverty Rate (%)']:.2f}<br>"
            f"% Without Vehicle: {row['% Without Vehicle']:.2f}"
        ), axis=1),
    hovertemplate="%{text}<extra></extra>")

highlight = None
if selected_county != "All" and selected_county in county_fips:
    selected_fips = county_fips[selected_county]
    selected_feature = next((f for f in geo_json["features"] if f["id"] == selected_fips), None)
    if selected_feature:
        highlight = go.Choropleth(
            geojson={"type": "FeatureCollection", "features": [selected_feature]},
            locations=[selected_fips],
            z=[0],
            colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']],
            showscale=False,
            marker_line_color="black",
            marker_line_width=2.5,
            featureidkey="id",
            hoverinfo="skip")

fig = go.Figure(data=[choropleth] + ([highlight] if highlight else []))
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(
    title="Percentage of Low-Income Low-Access (LILA) Tracts by Massachusetts County",
    margin={"r": 0, "t": 50, "l": 0, "b": 0})

st.subheader("🗺️ Food Access Map")
st.write("🔍 Sidebar: Select County to explore.")
st.write("📈 Chart: Zoom in and out of the map to explore. Hover each county for more information.")
st.plotly_chart(fig, use_container_width=True)

st.markdown(
    f"""
    <div style="background-color: #fdecea; padding: 1rem; border-radius: 0.5rem; text-align: left; color: #611a15; font-size: 16px;">
        💡 This map reveals that patterns of food access vary significantly across Massachusetts. Counties like Hampshire 
        may show higher rates of LILA tracts, signaling deeper food access challenges.<br>
    </div>""", unsafe_allow_html=True)


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
