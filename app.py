import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# Page configuration

st.set_page_config(
    page_title="Data Visualization Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("Bycicle Data Analysis 2011 - 2012 Dashboard HERNAN")
st.markdown("---")


## DATA

df = pd.read_csv('train.csv')
df["datetime"] = pd.to_datetime(df["datetime"])

df['year'] = df['datetime'].dt.year
df['month'] = df['datetime'].dt.month
df['day'] = df['datetime'].dt.day
df['hour'] = df['datetime'].dt.hour
df['dayofweek'] = df['datetime'].dt.dayofweek

# Months 
month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 
              5: 'May', 6: 'June', 7: 'July', 8: 'August',
              9: 'September', 10: 'October', 11: 'November', 12: 'December'}
df['month_name'] = df['month'].map(month_names)

# Days of week
day_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
            4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
df['dayofweek_name'] = df['dayofweek'].map(day_names)

# Season
season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
df['season_name'] = df['season'].map(season_map)

# Weather Conditions
weather_map = {1: 'Clear', 2: 'Cloudy', 3: 'Light Snow, Light Rain', 4: 'Heavy Rain, Snow'}
df['weather_condition'] = df['weather'].map(weather_map)




##  WIDGETS
st.sidebar.markdown("# Filters")
st.sidebar.markdown("---")



# 1. Hour range
selected_hours = st.sidebar.slider(
    "Select hour range",
    min_value=int(df['hour'].min()),
    max_value=int(df['hour'].max()),
    value=(int(df['hour'].min()), int(df['hour'].max())),
    step=1
)

# 2: Year
selected_years = st.sidebar.multiselect(
    "Select year",
    options=sorted(df['year'].unique()),
    default=sorted(df['year'].unique())
)

# 3: Month 
selected_months = st.sidebar.multiselect(
    "Select months",
    options=sorted(df['month_name'].unique())
    
)

# 4: Season
selected_seasons = st.sidebar.multiselect(
    "Select season",
    options=sorted(df['season_name'].unique())
    
)
# 5: Weather conditions 
selected_condition = st.sidebar.multiselect(
    "Weather conditions",
    options=sorted(df['weather_condition'].unique())
    
)

# 6: Working Day
selected_workingday = st.sidebar.multiselect(
    "Working Day",
    options=sorted(df['workingday'].unique()),   
       
)

st.sidebar.markdown("---")
st.sidebar.info("When select month, you cannoot select a diferent season")

# DATA FILTERING

filtered_df = df[
    (df['hour'] >= selected_hours[0]) &
    (df['hour'] <= selected_hours[1])
]

if selected_years:
    filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]

if selected_months:
    filtered_df = filtered_df[filtered_df['month_name'].isin(selected_months)]

if selected_seasons:
    filtered_df = filtered_df[filtered_df['season_name'].isin(selected_seasons)]

if selected_condition:
    filtered_df = filtered_df[filtered_df['weather_condition'].isin(selected_condition)]

if selected_workingday:
    filtered_df = filtered_df[filtered_df['workingday'].isin(selected_workingday)]    

def format_filter(name, values):
    if not values:
        return ""
    return f"{name}: {', '.join(str(v) for v in values)}"

active_filters = ", ".join(filter(None, [
    format_filter("Year", selected_years),
    format_filter("Month", selected_months),
    format_filter("Season", selected_seasons),
    format_filter("Weather", selected_condition)
]))


# 1. SUMMARY METRICS
title = "### Dataset Overview"
if active_filters:
    title += f" — {active_filters}"

st.markdown(title)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Records", f"{len(filtered_df):,}")

col2.metric("Average Users", f"{filtered_df['count'].mean():.0f}")

col3.metric("Avg. Temperature", f"{filtered_df['temp'].mean():.1f}°C")

col4.metric("Avg. Humidity", f"{filtered_df['humidity'].mean():.1f}%")

st.markdown("---")

# SECTION 2: INTERACTIVE CHARTS
title2 = "## Principal Visualizations"
if active_filters:
    title2 += f" — {active_filters}"

st.markdown(title2)


# Chart 1. Demand by Hour
col1, col2 = st.columns(2)

col1.subheader("Demand by Hour of Day")
hourly_demand = filtered_df.groupby('hour')['count'].mean().reset_index()
hourly_demand.columns = ['Hour', 'Average']

fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=hourly_demand['Hour'],
    y=hourly_demand['Average'],
    marker_color="#106BAC"
))
col1.plotly_chart(fig1, use_container_width=True)

# Chart 2: Demand by Month

col2.subheader("Demand by Month average")

month_order = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

monthly_demand = (
    filtered_df.groupby('month_name')['count']
    .mean()
    .reindex(month_order)
    .dropna()
)

fig2 = px.line(
    x=monthly_demand.index,
    y=monthly_demand.values,
    markers=True,
    labels={'x': 'Month', 'y': 'Average Users'},
)

fig2.update_traces(line=dict(color="#106BAC", width=3))
fig2.update_layout(height=400)

col2.plotly_chart(fig2, use_container_width=True)

# Chart 3: Distribution by Day of Week
col3, col4 = st.columns(2)

col3.subheader("Demand by Day of Week")
day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

day_demand = (
    filtered_df.groupby('dayofweek_name')['count']
    .mean()
    .reindex(day_order)
)

colors_days = [
    "#B4BC28" if day in ['Saturday','Sunday'] else '#4ECDC4'
    for day in day_demand.index
]

fig3 = go.Figure(data=[
    go.Bar(x=day_demand.index, y=day_demand.values, marker_color=colors_days)
])
col3.plotly_chart(fig3, use_container_width=True)
    
# Chart 4: Heatmap - Hour x Day of Week average
col4.subheader("Heatmap: Hour vs Day of Week average")

day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

heatmap_data = filtered_df.pivot_table(
    values='count',
    index='dayofweek_name',
    columns='hour',
    aggfunc='mean'
).reindex(day_order)

fig4 = go.Figure(data=go.Heatmap(
    z=heatmap_data.values,
    x=heatmap_data.columns,
    y=heatmap_data.index,
    colorscale='Blues'
))

fig4.update_layout(
    xaxis_title="Hour of Day",
    yaxis_title="Day of Week",
    height=400
)
col4.plotly_chart(fig4, use_container_width=True)

# Chart 5: Weather Variables
if len(filtered_df) > 0:
    st.subheader("Correlation Between Weather Variables")
    col5, col6 = st.columns(2)

    sample_size = min(500, len(filtered_df))
    sample_df = filtered_df.sample(sample_size)

    # Temperature vs Demand
    fig5 = px.scatter(
        sample_df,
        x='temp',
        y='count',
        color='hour',
        title='Temperature vs User Demand',
        labels={'temp': 'Temperature (°C)', 'count': 'Users'},
        color_continuous_scale='Viridis'
    )
    col5.plotly_chart(fig5, use_container_width=True)

    # Humidity vs Demand
    fig6 = px.scatter(
        sample_df,
        x='humidity',
        y='count',
        color='temp',
        title='Humidity vs User Demand',
        labels={'humidity': 'Humidity (%)', 'count': 'Users'},
        color_continuous_scale='Plasma'
    )
    col6.plotly_chart(fig6, use_container_width=True)

else:
    st.info("No data available for the selected filters.")

st.markdown("---")

#DATASET Download
st.markdown("### Filtered Dataset View")

# Expand to view data
with st.expander(" View complete data (filtered)", expanded=False):
    st.write(f"Showing {len(filtered_df)} records out of {len(df)} total")
    st.dataframe(filtered_df, use_container_width=True, height=400)

# Statistics
st.markdown("### Descriptive Statistics")

numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns.tolist()

st.write("**Numeric statistics**")
st.dataframe(filtered_df[numeric_cols].describe(), use_container_width=True)

