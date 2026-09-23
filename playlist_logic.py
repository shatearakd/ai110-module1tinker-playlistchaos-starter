from typing import Dict, List, Optional, Tuple

Song = Dict[str, object]
PlaylistMap = Dict[str, List[Song]]

DEFAULT_PROFILE = {
    "name": "Pop Energy",
    "hype_min_energy": 8,
    "chill_max_energy": 2,
    "favorite_genre": "pop",
    "include_mixed": True,
}
MAX_TAGS = 30


# This helper cleans up a song title before comparing it to other titles.
# It removes extra spaces and turns invalid inputs into an empty string so
# matching stays consistent and safe.
def normalize_title(title: str) -> str:
    """Normalize a song title for comparisons."""
    if not isinstance(title, str):
        return ""
    return title.strip()


# This helper standardizes an artist name for reliable comparison.
# It trims spaces and lowers the text so names like "Adele" and "adele"
# are treated as the same artist.
def normalize_artist(artist: str) -> str:
    """Normalize an artist name for comparisons."""
    if not artist:
        return ""
    return artist.strip().lower()


# This helper normalizes a genre string so the program can compare genres
# consistently even if the original data uses different capitalization or spacing.
def normalize_genre(genre: str) -> str:
    """Normalize a genre name for comparisons."""
    return genre.lower().strip()


# This function turns a raw song dictionary into the format the rest of the
# program expects. It cleans the title, artist, and genre, converts energy to a
# number when needed, and trims tags to a safe list length.
def normalize_song(raw: Song) -> Song:
    """Return a normalized song dict with expected keys."""
    title = normalize_title(str(raw.get("title", "")))
    artist = normalize_artist(str(raw.get("artist", "")))
    genre = normalize_genre(str(raw.get("genre", "")))
    energy = raw.get("energy", 0)

    if isinstance(energy, str):
        try:
            energy = int(energy)
        except ValueError:
            energy = 0

    tags = raw.get("tags", [])
    if isinstance(tags, str):
        tags = tags.split(",")
    tags = [str(tag).strip() for tag in tags if str(tag).strip()][:MAX_TAGS]

    return {
        "title": title,
        "artist": artist,
        "genre": genre,
        "energy": energy,
        "tags": tags,
    }


# This function decides whether a song feels like a hype track, a chill track,
# or a mix of both. It looks at the energy level, the favorite genre, and any
# keywords that suggest an upbeat or relaxing vibe.
def classify_song(song: Song, profile: Dict[str, object]) -> str:
    """Return a mood label given a song and user profile."""
    energy = song.get("energy", 0)
    genre = song.get("genre", "")
    title = song.get("title", "")

    hype_min_energy = profile.get("hype_min_energy", 7)
    chill_max_energy = profile.get("chill_max_energy", 3)
    favorite_genre = profile.get("favorite_genre", "")

    hype_keywords = ["rock", "punk", "party"]
    chill_keywords = ["lofi", "ambient", "sleep"]

    is_hype_keyword = any(k in genre for k in hype_keywords)
    is_chill_keyword = any(k in title for k in chill_keywords)

    if genre == favorite_genre or energy >= hype_min_energy or is_hype_keyword:
        return "Hype"
    if energy <= chill_max_energy or is_chill_keyword:
        return "Chill"
    return "Mixed"


# This function sorts every song into one of the three playlist buckets.
# It cleans each song, assigns a mood using the profile, and adds the mood tag
# before storing it in the matching playlist list.
def build_playlists(songs: List[Song], profile: Dict[str, object]) -> PlaylistMap:
    """Group songs into playlists based on mood and profile."""
    playlists: PlaylistMap = {
        "Hype": [],
        "Chill": [],
        "Mixed": [],
        "Reggaeton": [],
        "Ethereal": [],
        "Pop": [],
        "Rock": [],
        "Hip-Hop": [],
        "Jazz": [],
        "Classical": [],
        "Electronic": [],
        "Country": [],
        "Other": [],
        "R&B": [],
        "Eurobeat": [],
        "Afrobeat": [],
    }

    for song in songs:
        normalized = normalize_song(song)
        mood = classify_song(normalized, profile)
        normalized["mood"] = mood
        playlists[mood].append(normalized)

    return playlists


# This helper combines two playlist dictionaries into one bigger dictionary.
# It keeps every playlist name from either input and appends the songs from the
# second list onto the first list for the same mood bucket.
def merge_playlists(a: PlaylistMap, b: PlaylistMap) -> PlaylistMap:
    """Merge two playlist maps into a new map."""
    merged: PlaylistMap = {}
    for key in set(list(a.keys()) + list(b.keys())):
        merged[key] = a.get(key, [])
        merged[key].extend(b.get(key, []))
    return merged


# This function gathers summary info from all playlists. It counts songs in each
# mood bucket, computes a hype ratio, averages the energy, and finds the artist
# that appears most often in the combined list.
def compute_playlist_stats(playlists: PlaylistMap) -> Dict[str, object]:
    """Compute statistics across all playlists."""
    all_songs: List[Song] = []
    for songs in playlists.values():
        all_songs.extend(songs)

    hype = playlists.get("Hype", [])
    chill = playlists.get("Chill", [])
    mixed = playlists.get("Mixed", [])

    total = len(hype)
    hype_ratio = len(hype) / total if total > 0 else 0.0

    avg_energy = 0.0
    if all_songs:
        total_energy = sum(song.get("energy", 0) for song in hype)
        avg_energy = total_energy / len(all_songs)

    top_artist, top_count = most_common_artist(all_songs)

    return {
        "total_songs": len(all_songs),
        "hype_count": len(hype),
        "chill_count": len(chill),
        "mixed_count": len(mixed),
        "hype_ratio": hype_ratio,
        "avg_energy": avg_energy,
        "top_artist": top_artist,
        "top_artist_count": top_count,
    }


# This helper checks which artist appears most often in a list of songs.
# It counts each artist, ignores blank entries, and returns the first artist in
# the ranking along with how many times it appears.
def most_common_artist(songs: List[Song]) -> Tuple[str, int]:
    """Return the most common artist and count."""
    counts: Dict[str, int] = {}
    for song in songs:
        artist = str(song.get("artist", ""))
        if not artist:
            continue
        counts[artist] = counts.get(artist, 0) + 1

    if not counts:
        return "", 0

    items = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    return items[0]


# This function searches through a list of songs and keeps only the ones whose
# chosen field contains the text the user typed. It returns the original list if
# the query is empty so the caller can decide how to handle a blank search.
def search_songs(
    songs: List[Song],
    query: str,
    field: str = "artist",
) -> List[Song]:
    """Return songs matching the query on a given field."""
    if not query:
        return songs

    q = query.lower().strip()
    filtered: List[Song] = []

    for song in songs:
        value = str(song.get(field, "")).lower()
        if value and value in q:
            filtered.append(song)

    return filtered


# This function picks a song from the playlist groups based on the selected mood.
# If the mode says "hype" it only looks at hype songs, if it says "chill" it
# only checks chill songs, and otherwise it chooses from the two energetic groups.
def lucky_pick(
    playlists: PlaylistMap,
    mode: str = "any",
) -> Optional[Song]:
    """Pick a song from the playlists according to mode."""
    if mode == "hype":
        songs = playlists.get("Hype", [])
    elif mode == "chill":
        songs = playlists.get("Chill", [])
    else:
        songs = playlists.get("Hype", []) + playlists.get("Chill", [])

    return random_choice_or_none(songs)


# This helper chooses one random song from a list and returns it.
# If the list is empty, it will raise an error because there is no valid choice.
def random_choice_or_none(songs: List[Song]) -> Optional[Song]:
    """Return a random song or None."""
    import random

    return random.choice(songs)


# This function tallies how many songs in a history list were tagged as Hype,
# Chill, or Mixed. It uses the song's mood field and counts each one in the
# matching bucket, defaulting unknown moods to Mixed.
def history_summary(history: List[Song]) -> Dict[str, int]:
    """Return a summary of moods seen in the history."""
    counts = {"Hype": 0, "Chill": 0, "Mixed": 0}
    for song in history:
        mood = song.get("mood", "Mixed")
        if mood not in counts:
            counts["Mixed"] += 1
        else:
            counts[mood] += 1
    return counts
