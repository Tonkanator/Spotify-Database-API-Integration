import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Spotify API credentials
SPOTIFY_CLIENT_ID = "your_client_id"
SPOTIFY_CLIENT_SECRET = "your_client_secret"

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# Database setup
def init_db():
    conn = sqlite3.connect("music.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Artist (
            artist_id TEXT PRIMARY KEY,
            artist_name TEXT NOT NULL,
            artist_genre TEXT NOT NULL,
            artist_followers INTEGER NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Album (
            album_id TEXT PRIMARY KEY,
            album_title TEXT NOT NULL,
            album_total_tracks INTEGER NOT NULL,
            album_release_date TEXT NOT NULL,
            artist_id TEXT NOT NULL,
            FOREIGN KEY(artist_id) REFERENCES Artist(artist_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Track (
            track_id TEXT PRIMARY KEY,
            track_title TEXT NOT NULL,
            duration INTEGER NOT NULL,
            album_id TEXT NOT NULL,
            FOREIGN KEY(album_id) REFERENCES Album(album_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ArtistTrack (
            artist_id TEXT NOT NULL,
            track_id TEXT NOT NULL,
            PRIMARY KEY (artist_id, track_id),
            FOREIGN KEY (artist_id) REFERENCES Artist(artist_id),
            FOREIGN KEY (track_id) REFERENCES Track(track_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Playlist (
            playlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_name TEXT NOT NULL,
            creator TEXT NOT NULL,
            FOREIGN KEY(creator) REFERENCES user(username)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS PlaylistTrack (
            playlist_id INTEGER NOT NULL,
            track_id TEXT NOT NULL,
            track_number INTEGER NOT NULL,
            PRIMARY KEY (playlist_id, track_id),
            FOREIGN KEY(playlist_id) REFERENCES Playlist(playlist_id),
            FOREIGN KEY(track_id) REFERENCES Track(track_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS AlbumTrack (
            album_id TEXT NOT NULL,
            track_id TEXT NOT NULL,
            track_number INTEGER NOT NULL,
            PRIMARY KEY (album_id, track_id),
            FOREIGN KEY (album_id) REFERENCES Album(album_id),
            FOREIGN KEY (track_id) REFERENCES Track(track_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User (
            username TEXT NOT NULL PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

# Function to convert duration from ms to "0:00" format
def convert_duration(ms):
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    return f"{minutes}:{seconds:02d}"

# Fetch and save artists
def fetch_artists_and_save():
    conn = sqlite3.connect("music.db")
    cursor = conn.cursor()
    
    # List of genres to fetch artists from
    genres = ["pop", "rock", "hip-hop"]
    
    for genre in genres:
        print(f"Fetching artists in genre: {genre}")
        results = sp.search(q=f"genre:{genre}", type="artist", limit=15)
        for artist in results['artists']['items']:
            artist_id = artist['id']
            artist_name = artist['name']
            artist_genre = ', '.join(artist['genres'])
            artist_followers = artist['followers']['total']
            cursor.execute("""
                INSERT OR IGNORE INTO Artist (artist_id, artist_name, artist_genre, artist_followers)
                VALUES (?, ?, ?, ?)
            """, (artist_id, artist_name, artist_genre, artist_followers))
    
    conn.commit()
    conn.close()

# Fetch and save albums
def fetch_albums_and_save():
    conn = sqlite3.connect("music.db")
    cursor = conn.cursor()
    cursor.execute("SELECT artist_id FROM Artist")
    artist_ids = [row[0] for row in cursor.fetchall()]
    for artist_id in artist_ids:
        albums = sp.artist_albums(artist_id, album_type='album', limit=10)
        for album in albums['items']:
            album_id = album['id']
            album_title = album['name']
            album_total_tracks = album['total_tracks']
            album_release_date = album['release_date']
            cursor.execute("""
                INSERT OR IGNORE INTO Album (album_id, album_title, album_total_tracks, album_release_date, artist_id)
                VALUES (?, ?, ?, ?, ?)
            """, (album_id, album_title, album_total_tracks, album_release_date, artist_id))
    conn.commit()
    conn.close()

# Fetch and save tracks
def fetch_tracks_and_save():
    conn = sqlite3.connect("music.db")
    cursor = conn.cursor()
    cursor.execute("SELECT album_id FROM Album")
    album_ids = [row[0] for row in cursor.fetchall()]
    
    for album_id in album_ids:
        tracks = sp.album_tracks(album_id)
        
        for i, track in enumerate(tracks['items'], start=1):
            track_id = track['id']
            track_title = track['name']
            duration_formatted = convert_duration(track['duration_ms'])
            
            # Insert into Track table (assuming one artist for simplicity)
            cursor.execute("""
                INSERT OR IGNORE INTO Track (track_id, track_title, duration, album_id)
                VALUES (?, ?, ?, ?)
            """, (track_id, track_title, duration_formatted, album_id))
            
            # Insert into AlbumTrack for track order
            cursor.execute("""
                INSERT OR IGNORE INTO AlbumTrack (album_id, track_id, track_number)
                VALUES (?, ?, ?)
            """, (album_id, track_id, i))
            
            # Insert each artist associated with the track into ArtistTrack
            for artist in track['artists']:
                artist_id = artist['id']
                cursor.execute("""
                    INSERT OR IGNORE INTO ArtistTrack (artist_id, track_id)
                    VALUES (?, ?)
                """, (artist_id, track_id))
    
    conn.commit()
    conn.close()


# Fetch and save playlists from friends
def fetch_playlists_and_save():
    conn = sqlite3.connect("music.db")
    cursor = conn.cursor()

    # Spotify's user IDs of some friends
    user_ids = ["zls20qf1p1wy7k1gq1cme2hu9", "s4priv2nse8qnyqaxzk2iepqd", "jean.ez"]
    
    for id in user_ids:
        # Fetch playlists owned by friend
        playlists = sp.user_playlists(id, limit=2)['items']
        
        for playlist in playlists:
            spotify_playlist_id = playlist['id']
            playlist_name = playlist['name']
            playlist_creator = playlist['owner']['display_name']
            print(f"Fetching playlist: {playlist_name}")

            # Insert playlist into database
            cursor.execute("""
                INSERT OR IGNORE INTO Playlist (playlist_name, creator)
                VALUES (?, ?)
            """, (playlist_name, playlist_creator))
            
            # Retrieve playlist_id regardless of insert success
            cursor.execute("""
                SELECT playlist_id FROM Playlist WHERE playlist_name = ? AND creator = ?
            """, (playlist_name, playlist_creator))
            playlist_id = cursor.fetchone()[0]

            # Fetch tracks within the playlist
            tracks = sp.playlist_tracks(spotify_playlist_id)['items']

            track_number = 1
            
            for item in tracks:
                track = item['track']
                if track:
                    track_id = track['id']
                    track_title = track['name']
                    duration_formatted = convert_duration(track['duration_ms'])
                    album_id = track['album']['id']
                    
                    # Add the track to the Track table if it does not exist
                    cursor.execute("""
                        INSERT OR IGNORE INTO Track (track_id, track_title, duration, album_id)
                        VALUES (?, ?, ?, ?)
                    """, (track_id, track_title, duration_formatted, album_id))
                    
                    # Link the track to the playlist in the PlaylistTrack table
                    cursor.execute("""
                        INSERT OR IGNORE INTO PlaylistTrack (playlist_id, track_id, track_number)
                        VALUES (?, ?, ?)
                    """, (playlist_id, track_id, track_number))
                    track_number += 1

                    # Fetch artists associated with the track
                    for artist in track['artists']:
                        artist_id = artist.get('id')
                        artist_name = artist.get('name')

                        if not artist_id or not artist_name:
                            print(f"Skipping invalid artist data: {artist}")
                            continue

                        # Fetch additional artist information
                        try:
                            artist_details = sp.artist(artist_id)
                            artist_genre = ", ".join(artist_details['genres'])
                            artist_followers = artist_details['followers']['total']
                            
                            # Add the artist to the Artist table if it does not exist
                            cursor.execute("""
                                INSERT OR IGNORE INTO Artist (artist_id, artist_name, artist_genre, artist_followers)
                                VALUES (?, ?, ?, ?)
                            """, (artist_id, artist_name, artist_genre, artist_followers))
                        except Exception as e:
                            print(f"Error fetching artist details for {artist_id}: {e}")

    conn.commit()
    conn.close()


    
# Main function to populate the database
def populate_database():
    init_db()
    print("Fetching artists...")
    fetch_artists_and_save()
    print("Fetching albums...")
    fetch_albums_and_save()
    print("Fetching tracks...")
    fetch_tracks_and_save()
    print("Fetching playlists...")
    fetch_playlists_and_save()
    print("Database population complete!")

populate_database()