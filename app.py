import streamlit as st
import geopandas as gpd
import pandas as pd
from visuals import map_plot, bar_region, map_plot_filter_population, bar_state, summary_density

#load all necesary data
df = pd.read_csv("data/zus_POI.csv")
population_df = pd.read_csv("data/district_population_2024.csv")
gadm = gpd.read_file("data/gadm.geojson")
district_gdf = gpd.read_file("data/district.geojson")

df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

#configure
st.set_page_config(layout='wide')
st.title("ANALYSIS OF ZUS COFFEE STORE'S EXPANSION")
# Filter button
st.sidebar.header("FILTER") 
state = st.sidebar.multiselect(
    "Select state:",
    options=df["state"].unique(),
    default=df["state"].unique()
)
# --- District filter depends on state selection ---
if state:  # only show relevant districts
    district_options = df[df["state"].isin(state)]["district"].unique()
else:
    district_options = df["district"].unique()

district = st.sidebar.multiselect(
    "Select district:",
    options=district_options,
    default=district_options
)

df_selection = df_selection = df[(df["state"].isin(state)) &
                (df['district'].isin(district))
                ]

#load data as per df_selection
df_gdf = gpd.GeoDataFrame(df_selection,
                              geometry=gpd.points_from_xy(df_selection.longitude, df_selection.latitude),
                              crs="EPSG:4326")
df_gdf = df_gdf[~df_gdf.geometry.isna()]

#call visualization

map_plot_filter_population(df_gdf, gadm, district_gdf, population_df)
#bar_region(df_selection)
#bar_state(df_selection)
col1, col2 = st.columns(2)

with col1:
    fig1 = bar_state(df_selection)
    st.pyplot(fig1)

with col2:
    fig2 = bar_region(df_selection)
    st.pyplot(fig2)

result = summary_density(df_selection, population_df)
st.dataframe(result)

st.markdown("### ☕ **Underserved Areas — Possible Outlet Expansion?**")
st.markdown("""
- **Klang** – Only **2 stores / 100k citizen**; lots of untapped demand in residential and industrial zones.  
- **Johor Bahru** – **2 stores / 100k citizen**; a prime opportunity to capture commuter and tourist traffic from Singapore.  
- **Kuching** – **2 stores / 100k citizen**; minimal presence here considering Kuching as the capital city and the most busiest in Sarawak.  
- **Gombak** – **2 stores / 100k citizen**; high-density neighborhoods remain underserved.  

**Verdict:**  
- Prioritize **malls, transport hubs, and office/factories clusters** in Klang and Johor Bahru.  
""")

st.markdown("---")

st.markdown("### ⚠ **Saturated Areas — Focus on Optimization**")
st.markdown("""
- **Kuala Lumpur** – Already very densed, but yea KL cant never have enough of coffee chains 🤔 
- **Petaling** – Already very densed, but yea same with KL 
- **Sepang** – High density relative to population (probably due to it being an airport site ?); further expansion may not bring strong returns.  
- **Putrajaya** – Niche market (government officers and families); growth opportunities are limited here.  

**Verdict:**  
- Focus on **customer loyalty and retention** instead of new openings.  
- Use these saturated areas as **innovation labs** for testing premium formats or new services.  
""")

st.markdown("---")

st.markdown("### ✍️ **What's Next For This Analysis?**")
st.markdown("""
- Probably will add POI's on every ZUS COFFEE stores, can extract insight on the pattern of their openings; are they concentrated in malls, petrol pumps, or residentials?
- Will probably add another metrics; distance apart from every stores. This is to evaluate stores accessibility and cannibalization.
- Future analysis may include other coffee chain, overlay them in the same map and compare their density.
""")