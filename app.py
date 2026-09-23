import streamlit as st

from playlist_logic import (
    DEFAULT_PROFILE,
    MAX_TAGS,
    Song,
    build_playlists,
    compute_playlist_stats,
    history_summary,
    lucky_pick,
    merge_playlists,
    normalize_song,
    search_songs,
)

BASE_GENRES = ["rock", "lofi", "pop", "jazz", "electronic", "ambient", "other"]
PROFILE_PRESETS = {
    "Pop Energy": DEFAULT_PROFILE,
    "Workout Boost": {
        "name": "Workout Boost",
        "hype_min_energy": 7,
        "chill_max_energy": 2,
        "favorite_genre": "rock",
        "include_mixed": False,
    },
    "Focus Flow": {
        "name": "Focus Flow",
        "hype_min_energy": 9,
        "chill_max_energy": 4,
        "favorite_genre": "lofi",
        "include_mixed": True,
    },
    "Night Wind Down": {
        "name": "Night Wind Down",
        "hype_min_energy": 10,
        "chill_max_energy": 5,
        "favorite_genre": "ambient",
        "include_mixed": True,
    },
}


def genre_options():
    """Return built-in genres plus genres and tags already in the playlist."""
    options = BASE_GENRES[:]
    for song in st.session_state.songs:
        values = [song.get("genre", ""), *song.get("tags", [])]
        for value in values:
            value = str(value).strip()
            if value and value not in options:
                options.append(value)
    return options


def init_state():
    """Initialize Streamlit session state."""
    if "songs" not in st.session_state:
        st.session_state.songs = default_songs()
    # Normalize existing session data so stored artist names use title case.
    st.session_state.songs = [
        normalize_song(song) for song in st.session_state.songs
    ]
    if "profile" not in st.session_state:
        st.session_state.profile = dict(DEFAULT_PROFILE)
    if "profile_preset" not in st.session_state:
        st.session_state.profile_preset = DEFAULT_PROFILE["name"]
    if "loaded_profile_preset" not in st.session_state:
        st.session_state.loaded_profile_preset = DEFAULT_PROFILE["name"]
    if "history" not in st.session_state:
        st.session_state.history = []


def default_songs():
    """Return a default list of songs."""
    return [
        {
            "title": "Thunderstruck",
            "artist": "AC/DC",
            "genre": "rock",
            "energy": 9,
            "tags": ["classic", "guitar"],
        },
        {
            "title": "Lo-fi Rain",
            "artist": "DJ Calm",
            "genre": "lofi",
            "energy": 2,
            "tags": ["study"],
        },
        {
            "title": "Night Drive",
            "artist": "Neon Echo",
            "genre": "electronic",
            "energy": 6,
            "tags": ["synth"],
        },
        {
            "title": "Soft Piano",
            "artist": "Sleep Sound",
            "genre": "ambient",
            "energy": 1,
            "tags": ["sleep"],
        },
        {
            "title": "Bohemian Rhapsody",
            "artist": "Queen",
            "genre": "rock",
            "energy": 8,
            "tags": ["classic", "opera"],
        },
        {
            "title": "Blinding Lights",
            "artist": "The Weeknd",
            "genre": "pop",
            "energy": 8,
            "tags": ["synth", "dance"],
        },
        {
            "title": "Take Five",
            "artist": "Dave Brubeck",
            "genre": "jazz",
            "energy": 4,
            "tags": ["classic", "instrumental"],
        },
        {
            "title": "Strobe",
            "artist": "Deadmau5",
            "genre": "electronic",
            "energy": 7,
            "tags": ["progressive", "long"],
        },
        {
            "title": "Weightless",
            "artist": "Marconi Union",
            "genre": "ambient",
            "energy": 1,
            "tags": ["relax", "sleep"],
        },
        {
            "title": "Smells Like Teen Spirit",
            "artist": "Nirvana",
            "genre": "rock",
            "energy": 9,
            "tags": ["grunge", "90s"],
        },
        {
            "title": "Levitating",
            "artist": "Dua Lipa",
            "genre": "pop",
            "energy": 8,
            "tags": ["dance", "party"],
        },
        {
            "title": "So What",
            "artist": "Miles Davis",
            "genre": "jazz",
            "energy": 3,
            "tags": ["trumpet", "cool"],
        },
        {
            "title": "Midnight City",
            "artist": "M83",
            "genre": "electronic",
            "energy": 7,
            "tags": ["indie", "dream"],
        },
        {
            "title": "Gymnopedie No.1",
            "artist": "Erik Satie",
            "genre": "ambient",
            "energy": 1,
            "tags": ["piano", "calm"],
        },
        {
            "title": "Sweet Child O' Mine",
            "artist": "Guns N' Roses",
            "genre": "rock",
            "energy": 8,
            "tags": ["guitar", "80s"],
        },
        {
            "title": "Bad Guy",
            "artist": "Billie Eilish",
            "genre": "pop",
            "energy": 6,
            "tags": ["bass", "dark"],
        },
        {
            "title": "Fly Me to the Moon",
            "artist": "Frank Sinatra",
            "genre": "jazz",
            "energy": 5,
            "tags": ["vocal", "swing"],
        },
        {
            "title": "Sandstorm",
            "artist": "Darude",
            "genre": "electronic",
            "energy": 10,
            "tags": ["trance", "meme"],
        },
        {
            "title": "Clair de Lune",
            "artist": "Claude Debussy",
            "genre": "ambient",
            "energy": 2,
            "tags": ["piano", "classical"],
        },
        {
            "title": "Hotel California",
            "artist": "Eagles",
            "genre": "rock",
            "energy": 6,
            "tags": ["classic", "guitar"],
        },
        {
            "title": "Uptown Funk",
            "artist": "Mark Ronson ft. Bruno Mars",
            "genre": "pop",
            "energy": 9,
            "tags": ["funk", "dance"],
        },
        {
            "title": "Feeling Good",
            "artist": "Nina Simone",
            "genre": "jazz",
            "energy": 6,
            "tags": ["soul", "vocal"],
        },
        {
            "title": "Here Comes the Sun",
            "artist": "The Beatles",
            "genre": "rock",
            "energy": 6,
            "tags": ["classic", "uplifting"],
        },
        {
            "title": "Watermelon Sugar",
            "artist": "Harry Styles",
            "genre": "pop",
            "energy": 7,
            "tags": ["summer", "dance"],
        },
        {
            "title": "Electric Feel",
            "artist": "MGMT",
            "genre": "electronic",
            "energy": 7,
            "tags": ["indie", "synth"],
        },
        {
            "title": "Dreams",
            "artist": "Fleetwood Mac",
            "genre": "rock",
            "energy": 5,
            "tags": ["classic", "dreamy"],
        },
        {
            "title": "Lovely Day",
            "artist": "Bill Withers",
            "genre": "other",
            "energy": 6,
            "tags": ["soul", "uplifting"],
        },
    ]


def profile_sidebar():
    """Render and update the user profile."""
    st.sidebar.header("Mood profile")

    profile = st.session_state.profile
    selected_preset = st.sidebar.selectbox(
        "Recall profile",
        options=list(PROFILE_PRESETS),
        key="profile_preset",
    )
    if selected_preset != st.session_state.loaded_profile_preset:
        profile.clear()
        profile.update(PROFILE_PRESETS[selected_preset])
        st.session_state.loaded_profile_preset = selected_preset

    profile["name"] = st.sidebar.text_input(
        "Profile name",
        value=str(profile.get("name", "")),
    )

    col1, col2 = st.sidebar.columns(2)
    with col1:
        profile["hype_min_energy"] = st.sidebar.slider(
            "Hype min energy",
            min_value=1,
            max_value=10,
            value=int(profile.get("hype_min_energy", 7)),
        )
    with col2:
        profile["chill_max_energy"] = st.sidebar.slider(
            "Chill max energy",
            min_value=1,
            max_value=10,
            value=int(profile.get("chill_max_energy", 3)),
        )

    genres = genre_options()
    current_genre = profile.get("favorite_genre", genres[0])
    if current_genre not in genres:
        current_genre = genres[0]

    profile["favorite_genre"] = st.sidebar.selectbox(
        "Favorite genre",
        options=genres,
        index=genres.index(current_genre),
        format_func=lambda genre: str(genre).title(),
    )

    profile["include_mixed"] = st.sidebar.checkbox(
        "Include Mixed playlist in views",
        value=bool(profile.get("include_mixed", True)),
    )

    st.sidebar.write("Current profile:", profile["name"])


def add_song_sidebar():
    """Render the Add Song controls in the sidebar."""
    st.sidebar.header("Add a song")

    title = st.sidebar.text_input("Title")
    artist = st.sidebar.text_input("Artist")
    genre = st.sidebar.selectbox(
        "Genre",
        options=genre_options(),
    )
    energy = st.sidebar.slider("Energy", min_value=1, max_value=10, value=5)
    tags_text = st.sidebar.text_input("Tags (comma separated)")

    if st.sidebar.button("Add to playlist"):
        raw_tags = [t.strip() for t in tags_text.split(",")]
        tags = [t for t in raw_tags if t][:MAX_TAGS]

        song: Song = {
            "title": title,
            "artist": artist,
            "genre": genre,
            "energy": energy,
            "tags": tags,
        }
        if title and artist:
            normalized = normalize_song(song)
            all_songs = st.session_state.songs[:]
            all_songs.append(normalized)
            st.session_state.songs = all_songs


def playlist_tabs(playlists):
    """Render playlists in tabs."""
    include_mixed = st.session_state.profile.get("include_mixed", True)

    tab_labels = ["Hype", "Chill"]
    if include_mixed:
        tab_labels.append("Mixed")

    tabs = st.tabs(tab_labels)

    for label, tab in zip(tab_labels, tabs):
        with tab:
            render_playlist(label, playlists.get(label, []))


def render_playlist(label, songs):
    st.subheader(f"{label} playlist")
    # Playlist editors add normalized songs to the shared library, then refresh
    # this view so the active profile can classify the new song.
    if st.button(f"Edit {label} playlist", key=f"edit_playlist_{label}"):
        st.session_state.editing_playlist = label

    if st.session_state.get("editing_playlist") == label:
        with st.form(key=f"add_song_{label}"):
            st.write(f"Add a song to the {label} playlist")
            title = st.text_input("Title", key=f"edit_title_{label}")
            artist = st.text_input("Artist", key=f"edit_artist_{label}")
            genre = st.selectbox(
                "Genre",
                options=genre_options(),
                key=f"edit_genre_{label}",
            )
            energy = st.slider(
                "Energy",
                min_value=1,
                max_value=10,
                value=5,
                key=f"edit_energy_{label}",
            )
            tags_text = st.text_input(
                "Tags (comma separated)",
                key=f"edit_tags_{label}",
            )
            submitted = st.form_submit_button("Add song")

        if submitted:
            if not title.strip() or not artist.strip():
                st.error("Title and artist are required.")
            else:
                raw_tags = [tag.strip() for tag in tags_text.split(",")]
                song: Song = {
                    "title": title,
                    "artist": artist,
                    "genre": genre,
                    "energy": energy,
                    "tags": [tag for tag in raw_tags if tag][:MAX_TAGS],
                }
                st.session_state.songs = [
                    *st.session_state.songs,
                    normalize_song(song),
                ]
                st.session_state.editing_playlist = None
                st.rerun()

    if not songs:
        st.write("No songs in this playlist.")
        return

    query = st.text_input(f"Search {label} playlist by artist", key=f"search_{label}")
    filtered = search_songs(songs, query, field="artist")

    if not filtered:
        st.write("No matching songs.")
        return

    for song in filtered:
        mood = song.get("mood", "?")
        tags = ", ".join(song.get("tags", []))
        # Normalize legacy session data before displaying the artist name.
        display_artist = normalize_song(song)["artist"]
        st.write(
            f"- **{song['title']}** by {display_artist} "
            f"(genre {song['genre']}, energy {song['energy']}, mood {mood}) "
            f"[{tags}]"
        )


def lucky_section(playlists):
    """Render the lucky pick controls and result."""
    st.header("Lucky pick")

    mode = st.selectbox(
        "Pick from",
        options=["any", "hype", "chill"],
        index=0,
    )

    if st.button("Feeling lucky"):
        pick = lucky_pick(playlists, mode=mode)
        if pick is None:
            st.warning("No songs available for this mode.")
            return

        st.success(
            f"Lucky song: {pick['title']} by {pick['artist']} "
            f"(mood {pick.get('mood', '?')})"
        )

        history = st.session_state.history
        history.append(pick)
        st.session_state.history = history


def stats_section(playlists):
    """Render statistics based on the playlists."""
    st.header("Playlist stats")

    stats = compute_playlist_stats(playlists)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total songs", stats["total_songs"])
    col2.metric("Hype songs", stats["hype_count"])
    col3.metric("Chill songs", stats["chill_count"])

    col4, col5, col6 = st.columns(3)
    col4.metric("Mixed songs", stats["mixed_count"])
    col5.metric("Hype ratio", f"{stats['hype_ratio']:.2f}")
    col6.metric("Average energy", f"{stats['avg_energy']:.2f}")

    top_artist = stats["top_artist"]
    if top_artist:
        st.write(
            f"Most common artist: {top_artist} "
            f"({stats['top_artist_count']} songs)"
        )
    else:
        st.write("No top artist yet.")


def history_section():
    """Render the pick history overview."""
    st.header("History")

    history = st.session_state.history
    if not history:
        st.write("No history yet.")
        return

    summary = history_summary(history)
    st.write("Recent picks by mood:", summary)

    show_details = st.checkbox("Show full history")
    if show_details:
        for song in history:
            st.write(
                f"{song.get('mood', '?')}: {song['title']} by {song['artist']}"
            )


def clear_controls():
    """Render a small section for clearing data."""
    st.sidebar.header("Manage data")
    if st.sidebar.button("Reset songs to default"):
        st.session_state.songs = [
            normalize_song(song) for song in default_songs()
        ]
    if st.sidebar.button("Clear history"):
        st.session_state.history = []


def main():
    st.set_page_config(page_title="Playlist Chaos", layout="wide")
    st.title("Playlist Chaos")

    st.write(
        "An AI assistant tried to build a smart playlist engine. "
        "The code runs, but the behavior is a bit unpredictable."
    )

    init_state()
    profile_sidebar()
    add_song_sidebar()
    clear_controls()

    profile = st.session_state.profile
    songs = st.session_state.songs

    base_playlists = build_playlists(songs, profile)
    merged_playlists = merge_playlists(base_playlists, {})

    playlist_tabs(merged_playlists)
    st.divider()
    lucky_section(merged_playlists)
    st.divider()
    stats_section(merged_playlists)
    st.divider()
    history_section()


if __name__ == "__main__":
    main()
