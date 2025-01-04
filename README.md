# Spotify-Database-API-Integration

## Overview
This is a Python project that interacts with the Spotify Web API to fetch and store music data in an SQLite database. The project aims to create a relational database containing information about artists, albums, tracks, and playlists, allowing easy access to structured music data for further analysis or use.

## Installation
1. git clone https://github.com/Tonkanator/Spotify-Database-API-Integration.git
cd spotify-data-fetcher
2. pip install spotipy sqlite 3

## Usage
To use script (optional)
  1. Delete `music.db`
  2. Run the following command `python spotify-script.py`
3. Run the following command `python spotify-cli.py`

## Future Improvements
- Modify the code so that the search_db() function reuses the other search functions
- Divide matching search results into "pages" if many results are returned
- Create a UI in HTML/CSS and JavaScript
- Add support for fetching more genres and artist-related data
