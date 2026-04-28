import streamlit as st
import requests
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="MLB Highlight Architect", layout="wide")

# --- UI STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: white; }
    .stDateInput > div > div > input { background-color: #161B22; color: #58A6FF; }
    .game-card { 
        border: 1px solid #30363D; padding: 15px; border-radius: 10px; 
        background: #161B22; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("⚾ MLB Game & Highlight Viewer")
st.caption("Designed by Moses Effeyotah | INFO-6144 Web Development")

# --- DATE SELECTION ---
selected_date = st.date_input("Select Game Date", datetime.now())
date_str = selected_date.strftime("%Y-%m-%d")

# --- API LOGIC (Mirroring your index.html fetch) ---
@st.cache_data(ttl=3600) # Caches data for 1 hour to optimize performance
def get_mlb_games(date):
    url = f"https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date={date}"
    response = requests.get(url).json()
    return response.get("dates", [])[0].get("games", []) if response.get("dates") else []

games = get_mlb_games(date_str)

# --- DISPLAY ---
if not games:
    st.warning(f"No games found for {date_str}. Try another date.")
else:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📅 Today's Matchups")
        game_options = {f"{g['teams']['away']['team']['name']} @ {g['teams']['home']['team']['name']}": g['gamePk'] for g in games}
        selected_game_name = st.radio("Select a Game", list(game_options.keys()))
        selected_game_pk = game_options[selected_game_name]

    with col2:
        st.subheader("🎬 Highlights")
        # Fetching content for selected gamePk
        content_url = f"https://statsapi.mlb.com/api/v1/game/{selected_game_pk}/content"
        content = requests.get(content_url).json()
        
        highlights = content.get("highlights", {}).get("highlights", {}).get("items", [])
        
        if highlights:
            for item in highlights[:8]: # Top 8 highlights
                headline = item.get('headline', 'Great Play!')
            description = item.get('description', 'No description provided.')
                with st.expander(f"▶️ {item['headline']}"):
                    st.write(item['description'])
                    video_url = item['playbacks'][0]['url'] # Using playback index 0 as per your JS logic
                    st.video(video_url)
        else:
            st.info("No video highlights available for this game yet.")

# --- FOOTER ---
st.write("---")
st.markdown("**Architect Note:** This app utilizes the MLB Stats API to provide real-time sports telemetry and media delivery.")
