# aggregator.py
from collections import Counter

def aggregate_tracks(events, dorm=None, major=None, grade=None, top_n=20):
    """
    events: list of dicts with keys: spotify_id, track_id, title, artist, dorm, major, grade
    Returns list of {'track': 'Title - Artist', 'plays': N} sorted by plays desc
    """
    filtered = [
        e for e in events
        if (not dorm or e.get('dorm') == dorm)
        and (not major or e.get('major') == major)
        and (not grade or e.get('grade') == grade)
    ]
    counts = Counter(f"{e['title']} - {e['artist']}" for e in filtered)
    ranked = counts.most_common(top_n)
    return [{'track': t, 'plays': c} for t, c in ranked]