import streamlit as st
import sqlite3
from googleapiclient.discovery import build
import google.generativeai as genai
import os

# --- API & DB CONFIG ---
try:
    GOOGLE_API_KEY = st.secrets["google_api_key"]
    SEARCH_ENGINE_ID = st.secrets["search_engine_id"]
    GEMINI_API_KEY = st.secrets["gemini_api_key"]
    genai.configure(api_key=GEMINI_API_KEY)
except (KeyError, AttributeError):
    st.warning("API keys not found in st.secrets. Using dummy values for local dev.")
    GOOGLE_API_KEY = "dummy_google_api_key"
    SEARCH_ENGINE_ID = "dummy_search_engine_id"
    GEMINI_API_KEY = "dummy_gemini_api_key"

DB_FILE = 'requests.db'

# --- DATABASE SETUP & FUNCTIONS ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            thumbnail_url TEXT,
            source TEXT,
            date_requested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'Pending'
        )
    ''')
    conn.commit()
    conn.close()

def add_request(title, url, thumbnail_url, source):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO requests (title, url, thumbnail_url, source) VALUES (?, ?, ?, ?)", (title, url, thumbnail_url, source))
        conn.commit()
        st.success(f"Requested: {title}")
    except sqlite3.IntegrityError:
        st.warning("This item has already been requested.")
    finally:
        conn.close()

init_db()

# --- API FUNCTIONS ---
def google_search(query, **kwargs):
    if not query:
        return []
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    res = service.cse().list(q=query, cx=SEARCH_ENGINE_ID, searchType='image', **kwargs).execute()
    return res.get('items', [])

def get_refined_query(original_query):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    You are a helpful search assistant for a kid who wants to 3D print something.
    Your job is to take the user's raw idea and turn it into a concise, effective search query for finding 3D models.
    The query should use terms common in the 3D printing world.
    For example, if the user says "a fast car", a good refined query would be "racing car model print-in-place".
    If the user says "a little box for my toys", a good refined query would be "small toy container with lid".
    
    User's idea: "{original_query}"
    
    Refined search query:
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# --- PAGE CONFIG ---
st.set_page_config(page_title="Junior Print Scout", page_icon="🤖")

# --- SESSION STATE ---
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# --- PAGE SELECTION ---
page = st.sidebar.radio("Go to", ["Search", "Dad's Queue"])

# --- "KID" INTERFACE (SEARCH PAGE) ---
if page == "Search":
    st.title("Junior Print Scout 🤖")
    st.subheader("What do you want to build today?")

    user_input = st.text_input("Tell me what you're looking for!", key="user_input")

    if st.button("Ask Assistant"):
        if user_input:
            with st.spinner("Thinking of a better search..."):
                st.session_state.search_query = get_refined_query(user_input)
        else:
            st.warning("Please tell me what you want to build first!")

    if st.session_state.search_query:
        st.info(f"Search term: **{st.session_state.search_query}**")

    if st.button("Search Now!") or st.session_state.search_query:
        st.write("---")
        results = google_search(st.session_state.search_query, num=10)

        if not results:
            if st.session_state.search_query:
                st.warning(f"Oops! Couldn't find anything for '{st.session_state.search_query}'. Try a different search!")
        else:
            cols = st.columns(2)
            for i, result in enumerate(results):
                with cols[i % 2]:
                    title = result['title']
                    url = result['link']
                    thumbnail = result.get('pagemap', {}).get('cse_thumbnail', [{}])[0].get('src')
                    source = result['displayLink']

                    st.markdown(f"##### {title}")
                    if thumbnail:
                        st.image(thumbnail)
                    else:
                        st.caption("No image available")
                    
                    st.caption(f"Source: {source}")
                    
                    if st.button("Request This", key=f"req_{url}"):
                        add_request(title, url, thumbnail, source)
    
# --- "PARENT" INTERFACE (ADMIN PAGE) ---
elif page == "Dad's Queue":
    st.title("Dad's Print Queue 👨‍👧‍👦")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, title, url, thumbnail_url FROM requests WHERE status = 'Pending' ORDER BY date_requested ASC")
    requests = c.fetchall()

    if not requests:
        st.success("The print queue is empty! 🎉")
    else:
        for req_id, title, url, thumbnail_url in requests:
            st.write("---")
            col1, col2 = st.columns([1, 3])
            with col1:
                if thumbnail_url:
                    st.image(thumbnail_url, width=150)
            with col2:
                st.subheader(title)
                st.write(f"[Link to model]({url})")
                if st.button("Mark as Printed", key=f"print_{req_id}"):
                    c.execute("UPDATE requests SET status = 'Printed' WHERE id = ?", (req_id,))
                    conn.commit()
                    st.rerun()
    conn.close()