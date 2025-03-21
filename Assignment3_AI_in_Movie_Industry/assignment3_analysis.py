import os
import streamlit as st
import pandas as pd

# Must be the first Streamlit command
st.set_page_config(page_title="MokAInight", page_icon="🌙", layout="centered")

# ---------------------------------------
# 🔹 LOAD DATASET
# ---------------------------------------
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    complete_path = os.path.join(script_dir, "data", "movies_complete.csv")
    ratings_path = os.path.join(script_dir, "data", "movies.csv")

    if not os.path.exists(complete_path):
        st.error(f"File not found: {complete_path}. Make sure the dataset is in the data folder.")
        st.stop()

    df_main = pd.read_csv(complete_path)
    df_main["overview"] = df_main["overview"].fillna("")
    df_main["genres"] = df_main["genres"].fillna("")
    df_main["cast"] = df_main["cast"].fillna("")
    df_main["directors"] = df_main["directors"].fillna("")
    df_main["rating"] = pd.to_numeric(df_main.get("rating", 0), errors="coerce").fillna(0)
    df_main["release_date"] = pd.to_datetime(df_main.get("release_date", "1900-01-01"), errors="coerce")

    if os.path.exists(ratings_path):
        df_ratings = pd.read_csv(ratings_path)
        if "title" in df_ratings.columns and "age_rating" in df_ratings.columns:
            df_main = pd.merge(df_main, df_ratings[["title", "age_rating"]], on="title", how="left")
        else:
            st.warning("movies.csv found, but required columns ('title' and 'age_rating') are missing.")
    else:
        st.warning("movies.csv not found. Age ratings will not be available.")

    return df_main

# ---------------------------------------
# 🔹 FILTERING FUNCTIONS
# ---------------------------------------
def filter_by_genres(df, selected_genres):
    if not selected_genres:
        return df
    return df[df["genres"].apply(lambda x: any(genre in x for genre in selected_genres))]

def search_movies(df, query):
    if not query:
        return df
    query = query.lower()
    return df[
        df["title"].str.lower().str.contains(query) |
        df["cast"].str.lower().str.contains(query) |
        df["directors"].str.lower().str.contains(query)
    ]

def sort_top_rated(df):
    return df.sort_values(by="rating", ascending=False)

def sort_most_recent(df):
    return df.sort_values(by="release_date", ascending=False)

def surprise_sample(df, count=5):
    return df.sample(min(len(df), count))

# ---------------------------------------
# 🔹 DISPLAY FUNCTIONS
# ---------------------------------------
def show_movie_card(row):
    st.markdown(f"""
        <div class="movie-card">
            <h3>🎥 {row.title}</h3>
            <img src="{row.poster_url}" width="100%" class="movie-poster">
            <p><b>⭐ Rating:</b> {row.rating:.1f}</p>
            <p><b>📅 Release Date:</b> {row.release_date.date()}</p>
            <p><b>🎭 Genres:</b> {" ".join([f'<span class="genre-tag">{g}</span>' for g in row.genres.split(", ")])}</p>
            <p><b>🎭 Cast:</b> {row.cast}</p>
            <p><b>🎬 Directors:</b> {row.directors}</p>
            <p>{row.overview}</p>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------
# 🔹 MAIN APP FUNCTION
# ---------------------------------------
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, "data", "mokainight_logo.png")
    
    col1, col2 = st.columns([0.15, 0.85])
    with col1:
        st.image(logo_path, width=120)
    with col2:
        st.markdown("<h1 style='margin-top: 10px; font-size: 36px; font-weight: bold;'>MokAInight</h1>", unsafe_allow_html=True)
    st.write("<p style='font-size: 20px; font-weight: bold;'>Your AI-powered movie night companion.</p>", unsafe_allow_html=True)

    df = load_data()
    all_genres = sorted(df["genres"].dropna().str.split(", ").explode().unique().tolist())
    all_age_ratings = sorted(df["age_rating"].dropna().unique().tolist()) if "age_rating" in df.columns else []

    with st.container():
        st.markdown("<div style='max-width: 800px; margin: auto; font-size: 18px; font-weight: bold;'>", unsafe_allow_html=True)
        search_query = st.text_input("", placeholder="e.g. Inception, Leonardo DiCaprio, Nolan", label_visibility="collapsed")

        col_g1, col_g2 = st.columns([2, 1])
        with col_g1:
            selected_genres = st.multiselect("🎭 Select Genre(s):", all_genres)
        with col_g2:
            if all_age_ratings:
                selected_age_rating = st.selectbox("🧒 Age Rating:", ["All"] + all_age_ratings)
            else:
                selected_age_rating = "All"
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        filter_top_rated = st.checkbox("⭐ Top Rated")
    with col2:
        filter_most_recent = st.checkbox("📅 Most Recent")
    with col3:
        filter_surprise_me = st.checkbox("🎲 Surprise Me")

    st.markdown("""<div style='text-align: center; margin-top: 20px; width: 200px; margin-left: auto; margin-right: auto;'>""", unsafe_allow_html=True)
    show_button = st.button("🎬 Show Movies", key="show_movies", help="Click to find your next favorite movie!")
    st.markdown("""</div>""", unsafe_allow_html=True)

    if show_button:
        filtered_df = filter_by_genres(df, selected_genres)
        if selected_age_rating != "All":
            filtered_df = filtered_df[filtered_df["age_rating"] == selected_age_rating]
        filtered_df = search_movies(filtered_df, search_query)

        if filter_top_rated:
            filtered_df = sort_top_rated(filtered_df)
        if filter_most_recent:
            filtered_df = sort_most_recent(filtered_df)
        if filter_surprise_me:
            filtered_df = surprise_sample(filtered_df)

        if not filter_surprise_me:
            filtered_df = filtered_df.head(10)

        if not filtered_df.empty:
            st.subheader("🎬 Movie Recommendations")
            cols = st.columns(2)
            for i, row in enumerate(filtered_df.itertuples(), start=1):
                with cols[i % 2]:
                    show_movie_card(row)
        else:
            st.warning("No movies match your filters. Try adjusting your options.")

# ---------------------------------------
# 🔹 Custom Styling
# ---------------------------------------
st.markdown("""
    <style>
        label, .stTextInput > div, .stMultiSelect > div, .stCheckbox > div {
            font-size: 18px !important;
            font-weight: bold;
        }

        .stApp {
            background-color: #1e1e1e;
            background-image: url('https://www.transparenttextures.com/patterns/stardust.png');
            color: white;
        }
        .stMarkdown, .stTextInput, .stMultiSelect, .stCheckbox, .stButton > button {
            font-size: 18px !important;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------
# 🔹 Run App
# ---------------------------------------
if __name__ == "__main__":
    main()
