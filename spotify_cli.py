import sqlite3
import time

def print_menu(user, logged_in):
    time.sleep(1)
    
    print("\nCurrently logged in as: " + user)
    print("Choose one of the following: ")
    print("1. Search Database")
    print("2. Search Artists")
    print("3. Search Albums")
    print("4. Search Tracks")
    print("5. Search Playlists")
    print("6. View Artists")
    print("7. View Albums")
    print("8. View Tracks")
    print("9. View Playlists")
    if (not logged_in):
        print("10. Create Account")
        print("11. Log In")
    else:
        print("10. Create Playlist")
        print("11. Sign Out")

    print("-1. Exit")

def search_db(cursor):
    search = input("Search database: ")

    noMatch = True

    # Define the specific tables and columns to search
    search_targets = {
        "Artist": ["artist_name", "artist_genre"],
        "Album": ["album_title"],
        "Track": ["track_title"],
        "Playlist": ["playlist_name", "creator"]
    }

    # Dictionary to store results
    search_results = {
        "Artist": [],
        "Album": [],
        "Track": [],
        "Playlist": []
    }

    # Set to store unique playlist IDs to avoid duplicates
    playlist_ids_seen = set()

    # Iterate over each table and column to perform the search
    for table, columns in search_targets.items():
        for column in columns:
            query = f"SELECT * FROM {table} WHERE LOWER({column}) LIKE LOWER(?)"
            cursor.execute(query, (f'%{search}%',))
            matches = cursor.fetchall()

            # Store results in the dictionary
            if matches:
                # Special handling for Playlist to avoid duplicates where the playlist name is the same as creator by tracking playlist id
                if table == "Playlist":
                    for record in matches:
                        playlist_id = record[0]
                        if playlist_id not in playlist_ids_seen:
                            search_results[table].append(record)
                            playlist_ids_seen.add(playlist_id)
                else:
                    search_results[table].extend(matches)

                noMatch = False

    # Display the results
    if not noMatch:
        print(f"Search results for '{search}':\n")

        for table, records in search_results.items():
            time.sleep(1.25)
            if len(records) != 0:
                print(f"{table}")

                if table == "Artist":
                    print("(Artist ID | Artist Name)")
                    for record in records:
                        artist_id, artist_name = record[:2]
                        print(f"{artist_id} | {artist_name}")

                elif table == "Album":
                    print("(Album ID | Album Title | Artists)")
                    for record in records:
                        album_id, album_title = record[:2]
                        artist_id = record[-1]
                        cursor.execute("SELECT artist_name FROM Artist WHERE artist_id = ?", (artist_id,))
                        artist_name = cursor.fetchone()[0]
                        print(f"{album_id} | {album_title} | {artist_name}")

                elif table == "Track":
                    print("(Track ID | Track Title | Artist(s))")
                    for record in records:
                        track_id, track_title = record[:2]

                        # Fetch all artist names for this track
                        cursor.execute("""
                            SELECT Artist.artist_name 
                            FROM ArtistTrack
                            JOIN Artist ON ArtistTrack.artist_id = Artist.artist_id
                            WHERE ArtistTrack.track_id = ?
                        """, (track_id,))
                        artist_results = cursor.fetchall()

                        if artist_results:
                            artist_names = ', '.join(artist[0] for artist in artist_results)
                        else:
                            artist_names = "Unknown Artist"

                        # Print track information
                        print(f"{track_id} | {track_title} | {artist_names}")

                elif table == "Playlist":
                    print("(Playlist ID | Playlist Name | Creator)")
                    for record in records:
                        playlist_id, playlist_name, creator = record
                        print(f"{playlist_id} | {playlist_name} | {creator}")

                print()
    else:
        print(f"No matches found for '{search}'.")

def search_artists(cursor):
    search = input("Search Artists: ")

    results = []

    query = f"SELECT artist_id, artist_name FROM Artist WHERE LOWER(artist_name) LIKE LOWER(?)"
    cursor.execute(query, (f'%{search}%',))
    matches = cursor.fetchall()
    for match in matches:
        results.append((match))

    # Display the results
    if results:
        print(f"Search results for '{search}':\n")
        print("(Artist ID | Artist Name)")
        for result in results:
            artist_id, artist_name = result
            print(f"{artist_id} | {artist_name}")
    else:
        print(f"No matches found for '{search}'.")

    print()
    
def search_albums(cursor):
    search = input("Search Albums: ")

    results = []

    query = f"SELECT album_id, album_title, artist_id FROM Album WHERE LOWER(album_title) LIKE LOWER(?)"
    cursor.execute(query, (f'%{search}%',))
    matches = cursor.fetchall()
    for match in matches:
        results.append((match))

    # Display the results
    if results:
        print(f"Search results for '{search}':\n")
        print("(Album ID | Album Title | Artist)")
        for result in results:
            album_id, album_title, artist_id = result

            cursor.execute("SELECT artist_name FROM Artist WHERE artist_id = ?", (artist_id,))
            artist_name = cursor.fetchone()[0]
            print(f"{album_id} | {album_title} | {artist_name}")

    else:
        print(f"No matches found for '{search}'.")

    print()

def search_tracks(cursor):
    search = input("Search Tracks: ")

    results = []

    query = f"SELECT track_id, track_title FROM Track WHERE LOWER(track_title) LIKE LOWER(?)"
    cursor.execute(query, (f'%{search}%',))
    matches = cursor.fetchall()
    for match in matches:
        results.append((match))

    # Display the results
    if results:
        print(f"Search results for '{search}':\n")
        print("(Track ID | Track Title | Artist(s))")
        for result in results:
            track_id, track_title = result

            # Fetch all artist names for this track
            cursor.execute("""
                SELECT Artist.artist_name 
                FROM ArtistTrack
                JOIN Artist ON ArtistTrack.artist_id = Artist.artist_id
                WHERE ArtistTrack.track_id = ?
            """, (track_id,))
            artist_results = cursor.fetchall()

            if artist_results:
                artist_names = ', '.join(artist[0] for artist in artist_results)
            else:
                artist_names = "Unknown Artist"

            print(f"{track_id} | {track_title} | {artist_names}")
    else:
        print(f"No matches found for '{search}'.")

    print()

def search_playlists(cursor):
    search = input("Search Playlists: ")

    results = []

    query = f"SELECT * FROM Playlist WHERE LOWER(playlist_name) LIKE LOWER(?) OR LOWER(creator) LIKE LOWER(?)"
    cursor.execute(query, (f'%{search}%', f'%{search}%'))
    matches = cursor.fetchall()
    for match in matches:
        results.append((match))

    # Display the results
    if results:
        print(f"Search results for '{search}':\n")
        print("(Playlist ID | Playlist Name | Creator)")
        for result in results:
            playlist_id, playlist_name, creator = result
            print(f"{playlist_id} | {playlist_name} | {creator}")
    else:
        print(f"No matches found for '{search}'.")

    print()

def view_artist(cursor):
    artist_id = input("Enter the Artist ID: ")

    # Check if artist exists
    # Fetch artist name
    cursor.execute("SELECT artist_name, artist_genre, artist_followers FROM Artist WHERE artist_id = ?", (artist_id,))
    artist_result = cursor.fetchone()
    
    if not artist_result:
        print("Artist not found.")
        return
    
    artist_name, artist_genre, artist_followers = artist_result

    print(f"\nArtist: {artist_name}")
    print(f"Genres: {artist_genre}")
    print(f"Followers: {artist_followers}")

    # Fetch the albums from the artist
    cursor.execute("""
        SELECT album_id, album_title, album_total_tracks, album_release_date FROM Album WHERE artist_id = (?)
    """, (artist_id,))
    album_results = cursor.fetchall()

    if album_results:
        print("\nAlbums:")
        for album in album_results:
            album_id, album_title, album_total_tracks, album_release_date = album[:4]
            print(f"{album_id} | {album_title} | {album_total_tracks} | {album_release_date}")
    else:
        print("\nNo albums from this artist.")

    # Fetch all tracks associated with this artist
    cursor.execute("""
        SELECT Track.track_id, Track.track_title, Track.duration, Album.album_title
        FROM Track
        JOIN Album ON Track.album_id = Album.album_id
        JOIN ArtistTrack ON Track.track_id = ArtistTrack.track_id
        WHERE ArtistTrack.artist_id = ?
    """, (artist_id,))
    tracks = cursor.fetchall()

    if tracks:
        print("\nTracks:")
        print("( Track ID | Track Title | Duration | Album)")
        for track_id, track_title, duration, album_title in tracks:
            print(f"{track_id}| {track_title} | {duration} | {album_title}")
    else:
        print("No tracks found for this artist.")

def view_album(cursor):
    # Ask the user to input the album ID
    album_id = input("Enter the Album ID: ")

    # Fetch the album name and artist
    cursor.execute("""
        SELECT Album.album_title, Album.album_total_tracks, Album.album_release_date, Artist.artist_name 
        FROM Album
        JOIN Artist ON Album.artist_id = Artist.artist_id
        WHERE Album.album_id = ?
    """, (album_id,))
    
    album_info = cursor.fetchone()
    
    if not album_info:
        print("Album not found.")
        return
    
    album_title, album_total_tracks, album_release_date, artist_name = album_info
    print(f"\nAlbum: {album_title}")
    print(f"Total Tracks: {album_total_tracks}")
    print(f"Release Date: {album_release_date}")
    print(f"Artist: {artist_name}\n")

    # Fetch and display tracks in the album with their track numbers
    cursor.execute("""
        SELECT AlbumTrack.track_number, Track.track_title, Track.duration 
        FROM Track
        JOIN AlbumTrack ON Track.track_id = AlbumTrack.track_id
        WHERE AlbumTrack.album_id = ?
        ORDER BY AlbumTrack.track_number ASC
    """, (album_id,))
    
    tracks = cursor.fetchall()
    
    if not tracks:
        print("No tracks found in this album.")
        return
    
    for track_number, track_title, duration in tracks:
        print(f"{track_number}. {track_title} ({duration})")

def view_track(cursor):
    track_id = input("Enter the Track ID: ")

    # Check if the track exists
    cursor.execute("SELECT track_title, duration, album_id FROM Track WHERE track_id = ?", (track_id,))
    track_result = cursor.fetchone()

    if not track_result:
        print("Track not found.")
        return

    track_title, duration, album_id = track_result

    # Fetch album title
    cursor.execute("SELECT album_title FROM Album WHERE album_id = ?", (album_id,))
    album_data = cursor.fetchone()

    if album_data:
        album_title = album_data[0]
    else:
        album_title = "Single"

    print(f"\nTitle: {track_title}")
    print(f"Duration: {duration}\n")

    # Fetch all artists associated with this track
    cursor.execute("""
        SELECT Artist.artist_id, Artist.artist_name
        FROM Artist
        JOIN ArtistTrack ON Artist.artist_id = ArtistTrack.artist_id
        WHERE ArtistTrack.track_id = ?
    """, (track_id,))
    artist_results = cursor.fetchall()

    if artist_results:
        print("Artists:")
        print("(Artist ID | Artist Name)")
        for artist_id, artist_name in artist_results:
            print(f"{artist_id} | {artist_name}")
    else:
        print("No artists found for this track.")

    # Fetch all albums this track appears in
    cursor.execute("""
        SELECT Album.album_id, Album.album_title, Album.album_release_date
        FROM Album
        JOIN AlbumTrack ON Album.album_id = AlbumTrack.album_id
        WHERE AlbumTrack.track_id = ?
    """, (track_id,))
    album_results = cursor.fetchall()

    if album_results:
        print("\nAlbums:")
        print("(Album ID | Album Title | Release Date)")
        for album_id, album_title, release_date in album_results:
            print(f"{album_id} | {album_title} | {release_date}")
    else:
        print("No albums found for this track.")

def view_playlist(cursor):
    playlist_id = input("Enter the Playlist ID: ")

    tracks = []

    # Query to fetch the playlist name and creator
    cursor.execute("""
        SELECT playlist_name, creator
        FROM Playlist
        WHERE playlist_id = ?;
    """, (playlist_id,))
    
    # Fetch the playlist details
    playlist_details = cursor.fetchone()

    if not playlist_details:
        print("Playlist not found.")
        return
    
    playlist_name, creator = playlist_details

    # Query to fetch track details including track number, title, artist, and duration
    cursor.execute("""
        SELECT PT.track_number, T.track_title, T.duration, 
               GROUP_CONCAT(A.artist_name, ', ') AS artist_names
        FROM PlaylistTrack PT
        JOIN Track T ON PT.track_id = T.track_id
        LEFT JOIN ArtistTrack AT ON T.track_id = AT.track_id
        LEFT JOIN Artist A ON AT.artist_id = A.artist_id
        WHERE PT.playlist_id = ?
        GROUP BY PT.track_number, T.track_title, T.duration
        ORDER BY PT.track_number;
    """, (playlist_id,))
    
    # Fetch all matching tracks
    tracks = cursor.fetchall()

    # Display the results
    if tracks:
        print(f"Search results for '{playlist_id}':\n")

        print(f"Playlist: {playlist_name}")
        print(f"Created by: {creator}\n")

        for track_number, track_title, duration, artist_name, in tracks:
            print(f"{track_number}. {track_title} - {artist_name} ({duration})")
    else:
        print(f"No tracks found in this playlist.")

    print()

def create_playlist(cursor, creator):

    playlist_name = input("Enter the name of the playlist: ")

    cursor.execute("""
                INSERT INTO Playlist (playlist_name, creator)
                VALUES (?, ?)
            """, (playlist_name, creator))    
    
    print("Playlist sucessfully created.")

    # Get the generated playlist ID
    playlist_id = cursor.lastrowid
    print(f"Playlist '{playlist_name}' created with ID {playlist_id}.\n")

    track_number = 1

    while True:
        track_id = input("Enter the Track ID or -1 to exit: ")

        if track_id == "-1":
            break

        query = f"SELECT * FROM Track WHERE track_id = ?"
        cursor.execute(query, (f'{track_id}',))
        matches = cursor.fetchall()

        if matches == 0:
            print("No song of that Track ID exists.")
            pass

        cursor.execute("INSERT OR IGNORE INTO PlaylistTrack (playlist_id, track_id, track_number) VALUES (?, ?, ?)", (playlist_id, track_id, track_number))
        track_number += 1

        print("Track sucessfully added to the playlist.")

def create_account(cursor):
    valid = False

    while (valid != True):
        username = input("Enter your username: ")

        # Ensure the username isn't the command to exit
        if (username == "-1"):
            print("Invalid username.")
            pass

        query = f"SELECT * FROM User WHERE username = ?"
        cursor.execute(query, (f'{username}',))
        matches = cursor.fetchall()

        # Ensure username is unique
        if len(matches) != 0:
            print("Username is taken.")
            pass

        password = input ("Enter your password: ")
        query = f"SELECT * FROM User WHERE password = ?"
        cursor.execute(query, (f'{password}',))
        matches = cursor.fetchall()

        if len(matches) != 0:
                print("Password is taken.")
                pass
        
        break

    cursor.execute("""
                INSERT OR IGNORE INTO User (username, password)
                VALUES (?, ?)
            """, (username, password))    

    print("Account created sucessfully!")

def login(cursor):

    while True:
        username = input("Enter your username or -1 to exit: ")

        # Check if user wants t exit
        if username == "-1":
            return "-1"

        password = input("Enter your password: ")
        
        cursor.execute("SELECT * FROM User WHERE username = ? AND password = ?", (username, password,))
        matches = cursor.fetchone()

        if matches:
            return username
        else:
            print("Incorrect username or password.")

def main():
    conn = sqlite3.connect("music.db")
    cursor = conn.cursor()

    logged_in = False
    logged_user = "Guest"

    print("Welcome to my music streaming database!")

    while True:
        print_menu(logged_user, logged_in)
        choice = input()

        if choice == "1":
            search_db(cursor)
        elif choice == "2":
            search_artists(cursor)

        elif choice == "3":
            search_albums(cursor)

        elif choice == "4":
            search_tracks(cursor)

        elif choice == "5":
            search_playlists(cursor)

        elif choice == "6":
            view_artist(cursor)

        elif choice == "7":
            view_album(cursor)

        elif choice == "8":
            view_track(cursor)

        elif choice == "9":
            view_playlist(cursor)

        elif choice == "10" and logged_in == False:
            create_account(cursor)
            conn.commit()

        elif choice == "10" and logged_in == True:
            create_playlist(cursor, username)
            conn.commit()

        elif choice == "11" and logged_in == False:
            username = login(cursor)

            if username != "-1":
                print("Sucesfully logged in.")
                logged_in = True
                logged_user = username

        elif choice == "11" and logged_in == True:
            logged_in = False
            logged_user = "Guest"

        elif choice == "-1":
            conn.close()
            break

        else:
            print("Invalid choice. Enter a number from 1-7")

main()