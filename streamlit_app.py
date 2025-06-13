import streamlit as st
import pandas as pd
import altair as alt

df = pd.read_csv("Massachusetts Food Access Data - Sheet1.csv")
st.set_page_config(layout="wide")
st.title("🥘 Mapping Food Access in Massachusetts")

df["Pct_Households_No_Vehicle"] = (df["TractHUNV"] / df["OHU2010"]) * 100
df["LowAccessPopulation"] = df["LALOWI05_10"].fillna(0)

# Top 10 tracts by food inaccessibility
top10 = df.nlargest(10, "LowAccessPopulation")[["CensusTract", "County", "LowAccessPopulation"]]


# ───── Overview Section ─────
total_tracts = len(df)
percent_LILA = (df["LILATracts_1And10"].sum() / total_tracts) * 100
avg_poverty = df["PovertyRate"].mean()
avg_income = df["MedianFamilyIncome"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Census Tracts", f"{total_tracts}")
col2.metric("% LILA Tracts", f"{percent_LILA:.1f}%")
col3.metric("Avg Poverty Rate", f"{avg_poverty:.1f}%")
col4.metric("Avg Median Family Income", f"${avg_income:,.0f}")

# ───── Sidebar Filters ─────
st.sidebar.header("🔎 Filters")
counties = ["All"] + sorted(df["County"].dropna().unique())
selected_county = st.sidebar.selectbox("County", counties)
urban_only = st.sidebar.checkbox("Urban Tracts Only", value=False)
income_min = int(df["MedianFamilyIncome"].min())
income_max = int(df["MedianFamilyIncome"].max())
income_range = st.sidebar.slider("Median Income Range", min_value=income_min,
                                 max_value=income_max, value=(income_min, income_max))

# Apply filters
filtered = df.copy()
if selected_county != "All":
    filtered = filtered[filtered["County"] == selected_county]
if urban_only:
    filtered = filtered[filtered["Urban"] == 1]
filtered = filtered[(filtered["MedianFamilyIncome"] >= income_range[0]) &
                    (filtered["MedianFamilyIncome"] <= income_range[1])]

# ───── Charts: Income vs Poverty (Chart 1) + Vehicle Access (Chart 2) ─────
st.subheader("📊 Coordinated Visualizations")

brush = alt.selection_interval()

# Chart 1: Scatter Plot with Brushing
scatter = alt.Chart(filtered).mark_circle(opacity=0.7).encode(
    x=alt.X("MedianFamilyIncome:Q", title="Median Family Income"),
    y=alt.Y("PovertyRate:Q", title="Poverty Rate (%)"),
    size=alt.Size("Pop2010:Q", title="Population", scale=alt.Scale(range=[0, 100])),
    color=alt.Color("County:N", title="County"),
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
    tooltip=["mean(Pct_Households_No_Vehicle):Q"]
).properties(
    title="Chart 2: % Without Vehicles (From Brushed Scatter Selection)",
    width=600,
    height=400
)

# Chart 2B: Full fallback bar chart (unlinked)
bar_fallback = alt.Chart(filtered).mark_bar().encode(
    x=alt.X("mean(Pct_Households_No_Vehicle):Q", title="% Without Vehicle"),
    y=alt.Y("County:N", sort="-x", title="County"),
    tooltip=["mean(Pct_Households_No_Vehicle):Q"]
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



# ───── Chart 3: Top 10 Food Inaccessible Tracts ─────
st.subheader("🏙️ Top 10 Tracts with Highest Low-Access Population")

bar_top10 = alt.Chart(top10).mark_bar().encode(
    x=alt.X("LowAccessPopulation:Q", title="Low-Access Population"),
    y=alt.Y("CensusTract:N", sort="-x", title="Census Tract"),
    tooltip=["County", "LowAccessPopulation"]
).properties(
    width=700,
    height=400,
    title="Top 10 Tracts with Highest Food Inaccessibility"
)

st.altair_chart(bar_top10, use_container_width=True)

# ───── Key Takeaways Section ─────
with st.expander("📌 Key Takeaways and Reflections"):
    st.markdown("""
### 💡 Summary of Insights
- Tracts with **low median family income** and **high poverty rates** are often also classified as **Low-Income and Low Access (LILA)**.
- Lack of **vehicle access** adds another layer of difficulty in accessing grocery stores, especially in these high-need communities.
- The **top 10 most food-inaccessible tracts** span multiple counties, revealing that this is not just an urban or rural issue — it's widespread.

### 🩺 Health Implications
Food insecurity contributes to:
- Higher rates of **chronic disease** (e.g. diabetes, hypertension)
- Poor **mental health outcomes**
- Increased healthcare costs and systemic strain

### 🏛️ Policy & Equity Considerations
- Data like this should inform **grocery store placements**, **transportation subsidies**, and **SNAP/WIC outreach**.
- Equity-focused infrastructure investment can reduce access gaps.

### 🌎 Beyond Massachusetts
While this dashboard focuses on Massachusetts, similar patterns exist nationwide.  
A more just food system means confronting **transportation**, **poverty**, **zoning laws**, and **health disparities** together.
    """)

'''
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

st.altair_chart(chart1, use_container_width=True) '''

