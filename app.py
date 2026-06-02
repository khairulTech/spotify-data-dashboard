import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Data Portfolio | Spotify Analysis", layout="wide", page_icon="🎵")

st.title("🎵 Sound Tracked: My Spotify Listening Behavior")
st.markdown("""
### An Exploratory Data Analysis Portfolio Project
This dashboard processes my personal Spotify streaming history to extract consumption trends, engagement metrics, and daily audio habits.
""")
st.markdown("---")

# 2. Data Preprocessing Pipeline
@st.cache_data
def load_and_clean_data():
    # Load the raw JSON data you just downloaded
    df = pd.read_json("StreamingHistory_music_1.json")
    
    # Data Cleaning: Convert end time string to datetime object
    df['endTime'] = pd.to_datetime(df['endTime'])
    
    # Feature Engineering: Convert milliseconds to minutes
    df['minutes_played'] = df['msPlayed'] / 60000
    
    # Extract time attributes for analysis
    df['hour'] = df['endTime'].dt.hour
    df['day_of_week'] = df['endTime'].dt.day_name()
    
    # Filter out accidental clicks/skips (songs played less than 10 seconds)
    df = df[df['msPlayed'] > 10000]
    return df

# Run the data pipeline
# Replace the bottom part of your app.py with this:
try:
    df = load_and_clean_data()

    # 3. High-Level Metrics (KPI Cards)
    st.subheader("📊 Executive Summary")
    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        total_hours = int(df['minutes_played'].sum() / 60)
        st.metric(label="Total Hours Streamed", value=f"{total_hours:,} hrs")
    with kpi2:
        top_artist = df['artistName'].mode()[0]
        st.metric(label="Most Played Artist", value=top_artist)
    with kpi3:
        unique_tracks = df['trackName'].nunique()
        st.metric(label="Unique Songs Explored", value=f"{unique_tracks:,}")

    st.markdown("---")

    # 4. Interactive Charts
    st.subheader("📈 Behavioral Deep Dives")
    vis_col1, vis_col2 = st.columns(2)

    with vis_col1:
        st.markdown("**Peak Listening Hours** (When am I most active?)")
        hourly_counts = df.groupby('hour').size().reset_index(name='Streams')
        fig_hour = px.bar(hourly_counts, x='hour', y='Streams', 
                          labels={'hour': 'Hour of Day (24h)', 'Streams': 'Count of Streams'},
                          color='Streams', color_continuous_scale='darkmint')
        st.plotly_chart(fig_hour, use_container_width=True, key="hourly_chart")

    with vis_col2:
        st.markdown("**Top 10 Heavy Rotation Artists**")
        top_artists = df.groupby('artistName')['minutes_played'].sum().reset_index()
        top_artists = top_artists.sort_values(by='minutes_played', ascending=False).head(10)
        fig_artist = px.bar(top_artists, x='minutes_played', y='artistName', orientation='h',
                            labels={'minutes_played': 'Total Minutes', 'artistName': 'Artist'},
                            color='minutes_played', color_continuous_scale='tealgrn')
        fig_artist.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_artist, use_container_width=True, key="artist_chart")

    st.markdown("---")

    # 5. Raw Data Inspection Box
    st.subheader("🛠️ The Pipeline Transparency")
    with st.expander("Click here to view the underlying cleaned data frame"):
        st.dataframe(df[['endTime', 'artistName', 'trackName', 'minutes_played', 'day_of_week']].head(50))

except FileNotFoundError:
    st.error("⚠️ StreamingHistory_music_1.json was not found in this folder. Please verify the file name and location.")

