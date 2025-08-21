import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import geopandas as gpd

def map_plot(df_gdf, gadm, district_gdf):
    st.subheader("Zus Coffee Stores Across Malaysia") 
    fig, ax = plt.subplots(figsize=(30,38)) 
    gadm.boundary.plot(ax=ax, color="green", linewidth=1) 
    #state_gdf.boundary.plot(ax=ax, color="red", linewidth=1) 
    #district_gdf.boundary.plot(ax=ax, color="yellow", linewidth=1) 
    df_gdf.plot(ax=ax, color="blue", markersize=2, alpha=1) 
    ax.set_axis_off() 
    st.pyplot(fig, use_container_width=True)

def bar_state(df_selection):
    st.subheader("Total Stores for Every States")
    #col1, col2, col3 = st.columns([1, 4, 1])
    by_state = (df_selection['state']
                    .value_counts()
                    .reset_index(name="stores_count")
                    .rename(columns={"index":"state"})
    )

     # Create a color palette that maps from low to high values
    norm = plt.Normalize(by_state['stores_count'].min(),
                        by_state['stores_count'].max())
    colors = sns.color_palette("YlOrRd", as_cmap=True)(norm(by_state['stores_count']))

    #with col2:
    fig, ax = plt.subplots(figsize=(16,6))
    sns.barplot(
            data=by_state,
            x='stores_count',
            y='state',
            palette = colors,
            ax=ax
    )
    for i, v in enumerate(by_state['stores_count']):
        ax.text(v + (v * 0.01), i, f"{v:.0f}", color='black', va='center')
    ax.set_xlabel("Total Stores")
    ax.set_ylabel("State")
    return fig

def bar_region(df_selection):
    st.subheader("Top 5 District with Highest ZUS COFFEE Outlet")
    #col1, col2, col3 = st.columns([1, 4, 1])
    top_district = (df_selection['district']
                    .value_counts()
                    .nlargest(5)
                    .reset_index(name="stores_count")
                    .rename(columns={"index":"district"})
    )


     # Create a color palette that maps from low to high values
    norm = plt.Normalize(top_district['stores_count'].min(),
                        top_district['stores_count'].max())
    colors = sns.color_palette("YlOrRd", as_cmap=True)(norm(top_district['stores_count']))

    #with col2:
    fig, ax = plt.subplots(figsize=(6,2))
    sns.barplot(
            data=top_district,
            x='stores_count',
            y='district',
            palette = colors,
            ax=ax
    )
    for i, v in enumerate(top_district['stores_count']):
        ax.text(v + (v * 0.01), i, f"{v:.0f}", color='black', va='center')
    ax.set_xlabel("Total Stores")
    ax.set_ylabel("District")
    return fig

def map_folium(df_gdf, gadm, district_gdf):
    st.title("Zus Coffee Stores Across Malaysia")
    
    # Create base map centered on Malaysia
    m = folium.Map(
        location=[4.2105, 101.9758],  # Center of Malaysia
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # Add country boundary
    folium.GeoJson(
        gadm,
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': 'green',
            'weight': 2,
            'fillOpacity': 0
        }
    ).add_to(m)
    
    # Add district boundaries
    folium.GeoJson(
        district_gdf,
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': 'yellow',
            'weight': 1,
            'fillOpacity': 0
        }
    ).add_to(m)
    
    # Add coffee store points
    for idx, row in df_gdf.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=3,
            popup=f"Store: {row.get('name', 'address')}",  # Adjust column name as needed
            color='blue',
            fill=True,
            fillColor='blue',
            fillOpacity=0.8
        ).add_to(m)
    
    # Display the map in Streamlit
    map_data = st_folium(m, width=700, height=500)

    return map_data
    
def map_plot_filter(df_gdf, gadm, district_gdf):
    st.subheader("Zus Coffee Stores Across Malaysia")

    # Get unique states for dropdown (adjust column name as needed)
    state_column = 'NAME_1'  # Change this to match your actual state column in gadm
    state_names = sorted(gadm[state_column].unique())
    
    # Add "All States" option
    state_options = ['All States'] + list(state_names)
    
    # Create dropdown
    selected_state = st.selectbox(
        "Select a state to zoom in:",
        options=state_options,
        index=0  # Default to "All States"
    )
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(20, 38))
    
    if selected_state == 'All States':
        # Show all of Malaysia
        gadm.boundary.plot(ax=ax, color="green", linewidth=1)
        district_gdf.boundary.plot(ax=ax, color="yellow", linewidth=0.3)  # Uncomment if needed
        df_gdf.plot(ax=ax, color="blue", markersize=2, alpha=1)
        
    else:
        # Filter gadm for selected state
        selected_state_boundary = gadm[gadm[state_column] == selected_state]
        
        # Filter coffee stores for selected state using spatial intersection
        selected_stores = df_gdf[df_gdf.intersects(selected_state_boundary.unary_union)]
        
        # Plot the filtered data
        selected_state_boundary.boundary.plot(ax=ax, color="green", linewidth=2)
        # Optionally show districts in selected state
        selected_districts = district_gdf[district_gdf.intersects(selected_state_boundary.unary_union)]
        selected_districts.boundary.plot(ax=ax, color="yellow", linewidth=1)
        
        selected_stores.plot(ax=ax, color="blue", markersize=20, alpha=1)  # Slightly larger markers for zoomed view
        
        # Set the plot bounds to the selected state
        bounds = selected_state_boundary.total_bounds
        ax.set_xlim(bounds[0], bounds[2])  # min_x, max_x
        ax.set_ylim(bounds[1], bounds[3])  # min_y, max_y
        
        # Show store count for selected state
        st.info(f"**{len(selected_stores)} Zus Coffee stores** found in {selected_state}")
    
    ax.set_axis_off()
    st.pyplot(fig, use_container_width=True)
    
    return selected_state

def map_plot_filter_population(df_gdf, gadm, district_gdf, population_df):
    st.subheader("Distribution of ZUS's Outlet with Population Density")

    # Get unique states for dropdown (adjust column name as needed)
    state_column = 'NAME_1'  # Change this to match your actual state column in gadm
    state_names = sorted(gadm[state_column].unique())
    
    # Add "All States" option
    state_options = ['All States'] + list(state_names)
    
    # Create dropdown
    selected_state = st.selectbox(
        "Select a state to zoom in:",
        options=state_options,
        index=0  # Default to "All States"
    )
    
    # Add checkbox for population heatmap
    show_population = st.checkbox("Show population heatmap", value=True)
    population_df['population'] = population_df['population'] * 1000
    # Merge district_gdf with population data
    # Adjust the column names to match your actual data
    district_with_pop = district_gdf.merge(
        population_df, 
        left_on='NAM',  # Adjust this to match your district column name
        right_on='district',  # Adjust this to match your population df column name
        how='left'
    )
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(20, 38))
    
    if selected_state == 'All States':
        # Show all of Malaysia
        if show_population:
            # Plot population heatmap
            district_with_pop.plot(
                ax=ax, 
                column='population',  # Adjust column name as needed
                cmap='Reds',  # Color scheme for population
                alpha=0.7,
                legend=True,
                legend_kwds={'shrink': 0.6, 'aspect': 20}
            )
        else:
            # Just show district boundaries
            district_gdf.boundary.plot(ax=ax, color="lightgray", linewidth=0.3)
        
        # State boundaries on top
        gadm.boundary.plot(ax=ax, color="green", linewidth=1)
        
        # Coffee stores on top
        df_gdf.plot(ax=ax, color="blue", markersize=2, alpha=1)
        
    else:
        # Filter gadm for selected state
        selected_state_boundary = gadm[gadm[state_column] == selected_state]
        
        # Filter coffee stores for selected state using spatial intersection
        selected_stores = df_gdf[df_gdf.intersects(selected_state_boundary.unary_union)]
        
        # Filter districts for selected state
        selected_districts_with_pop = district_with_pop[
            district_with_pop.intersects(selected_state_boundary.unary_union)
        ]
        
        if show_population:
            # Plot population heatmap for selected state
            selected_districts_with_pop.plot(
                ax=ax, 
                column='population',  # Adjust column name as needed
                cmap='Reds',
                alpha=0.7,
                legend=True,
                legend_kwds={'shrink': 0.6, 'aspect': 20}
            )
        else:
            # Just show district boundaries
            selected_districts_with_pop.boundary.plot(ax=ax, color="lightgray", linewidth=0.5)
        
        # State boundary on top
        selected_state_boundary.boundary.plot(ax=ax, color="green", linewidth=2)
        
        # Coffee stores on top
        selected_stores.plot(ax=ax, color="blue", markersize=20, alpha=1)
        
        # Set the plot bounds to the selected state
        bounds = selected_state_boundary.total_bounds
        ax.set_xlim(bounds[0], bounds[2])  # min_x, max_x
        ax.set_ylim(bounds[1], bounds[3])  # min_y, max_y
        
        # Show store count for selected state
        total_pop = selected_districts_with_pop['population'].sum()
        st.info(f"**{len(selected_stores)} Zus Coffee stores** found in {selected_state}")
        #if show_population and not pd.isna(total_pop):
            #st.info(f"**Total population: {total_pop:,.0f}** in {selected_state}")
    
    ax.set_axis_off()
    
    # Add title and legend adjustments
    if show_population:
        plt.title("Zus Coffee Stores (Blue) and Population Density by District", 
                 fontsize=16, pad=20)
    else:
        plt.title("Zus Coffee Stores Across Malaysia", fontsize=16, pad=20)
    
    st.pyplot(fig, use_container_width=True)
    
    return selected_state

def summary_density(df_selection, population_df):
    st.title("Density Analysis")
    st.markdown("(PS: Sabah's is excluded from this analysis due to data discrepancy)")
    #population_df = population_df.copy()
    population_df['population'] = pd.to_numeric(population_df['population'], errors = 'coerce')
    population_df['population (mil)'] = (population_df['population'] / 1_000_000).round(3)
    #population_df = population_df.rename(columns={"population": "population (mil)"})

    # Count stores per district
    district_stcount = (
        df_selection['district']
        .value_counts()
        .reset_index(name="store_count")
        .rename(columns={"index": "district"})
    )

    # Merge with population
    merged = pd.merge(district_stcount, population_df, on="district", how="left")

    # Convert to numeric safely
    merged['store_count'] = pd.to_numeric(merged['store_count'], errors='coerce').fillna(0).astype(int)
    # Calculate density (stores per 1M people), rounded to integer
    merged['density_100k'] = (merged['store_count'] / merged['population (mil)'] / 10).round(0)

    # Sort by density
    merged = merged.fillna(0).sort_values(by='density_100k', ascending=False).reset_index(drop=True)\
    .rename(columns={'district':'District',
                     'store_count':'Total Store',
                     'population (mil)':'Population (mil) as of 2024',
                     'density_100k':'Density per 100k Population'})

    return merged[['District', 'Total Store', 'population', 'Population (mil) as of 2024', 'Density per 100k Population']]