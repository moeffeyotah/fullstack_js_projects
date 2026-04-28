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

# --- API LOGIC ---
@st.cache_data(ttl=3600)
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
        content_url = f"https://statsapi.mlb.com/api/v1/game/{selected_game_pk}/content"
        content = requests.get(content_url).json()
        
        highlights_items = content.get("highlights", {}).get("highlights", {}).get("items", [])
        
        if highlights_items:
            for item in highlights_items[:8]:
                # Using .get() ensures the app doesn't crash if a field is missing
                safe_headline = item.get('headline', 'Great Play!')
                safe_description = item.get('description', 'No description provided.')
                
                with st.expander(f"▶️ {safe_headline}"):
                    st.write(f"*{safe_description}*")
                    
                    playbacks = item.get('playbacks', [])
                    video_url = None
                    
                    if playbacks:
                        # Find the first playback URL that contains '.mp4'
                        for p in playbacks:
                            url = p.get('url', '')
                            if ".mp4" in url:
                                video_url = url
                                break
                    
                    if video_url:
                        st.video(video_url)
                    else:
                        st.warning("Video playback format not supported for this clip.")
        else:
            st.info("No video highlights available for this game yet. Check back after the first pitch!")

# --- FOOTER ---
st.write("---")
st.markdown("**Architect Note:** This app utilizes the MLB Stats API to provide real-time sports telemetry and media delivery.")
