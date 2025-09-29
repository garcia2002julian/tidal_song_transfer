import tidalapi
import os
import csv
import re

# Global session object, will be reassigned for each user
session = tidalapi.Session()

def search_tidal_song(song_name, artist_name):
    """Searches for a song on Tidal and returns the best match's ID."""
    # Sanitize song name for better search results
    song_name = re.sub(r'\s*\(.*?\)', '', song_name)
    query = f"{song_name} {artist_name}"
    
    try:
        results = session.search(query=query, models=[tidalapi.media.Track], limit=5)
    except Exception as e:
        print(f"Error searching for '{query}': {e}")
        return None

    if not results['tracks']:
        with open('log.txt', 'a', encoding='utf-8') as f:
            f.write(f"No results found for {song_name} by {artist_name}\n")
        print(f"No results found for {song_name} by {artist_name}")
        return None

    # Simple matching logic: prioritize exact matches, then close names
    best_match = results['tracks'][0] # Default to first result
    for track in results['tracks']:
        if track.name.lower() == song_name.lower() and track.artist.name.lower() == artist_name.lower():
            best_match = track
            break # Found perfect match

    track = best_match
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(f"Found: {track.name} by {track.artist.name} (ID: {track.id}) for Spotify song: {song_name} by {artist_name}\n")

    if song_name.lower() != track.name.lower() or artist_name.lower() != track.artist.name.lower():
        with open('log2.txt', 'a', encoding='utf-8') as f:
            f.write(f"Name mismatch: TIDAL: {track.name} by {track.artist.name} || SPOTIFY: {song_name} by {artist_name}\n")
            
    return track.id

def transfer_songs(csv_filepath):
    """Handles the entire transfer process for a single user, replicating playlist structure from the CSV."""
    global session
    session = tidalapi.Session()
    
    print(f"\nLogging in for file: {os.path.basename(csv_filepath)}")
    print('Please follow the instructions in your browser to log in to Tidal.')
    session.login_oauth_simple()

    if not session.check_login():
        print("Login failed. Skipping this file.")
        return
    
    print("Login successful!")

    # 1. Read CSV and group songs by playlist
    spotify_playlists = {}
    print(f"Reading and grouping songs from {os.path.basename(csv_filepath)}...")
    with open(csv_filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader) # Skip header
        try:
            # Find column indices dynamically
            track_idx = header.index('Track name')
            artist_idx = header.index('Artist name')
            playlist_idx = header.index('Playlist name')
        except ValueError as e:
            print(f"CSV format error: Missing column - {e}. Please ensure 'Track name', 'Artist name', and 'Playlist name' columns exist.")
            return

        for row in reader:
            if not row: continue
            playlist_name = row[playlist_idx]
            song_info = (row[track_idx], row[artist_idx])
            if playlist_name not in spotify_playlists:
                spotify_playlists[playlist_name] = []
            spotify_playlists[playlist_name].append(song_info)
    
    print(f"Found {len(spotify_playlists)} unique playlists in the CSV file.")

    # 2. Get existing Tidal playlists to avoid duplicates
    tidal_playlists = {p.name: p for p in session.user.playlists()}

    # 3. Iterate through Spotify playlists and transfer songs
    for playlist_name, songs in spotify_playlists.items():
        print(f"\nProcessing playlist: '{playlist_name}' with {len(songs)} songs.")
        target_playlist = None

        # Find or create the playlist on Tidal
        if playlist_name in tidal_playlists:
            print(f"Playlist '{playlist_name}' already exists on Tidal.")
            target_playlist = tidal_playlists[playlist_name]
        else:
            print(f"Creating playlist '{playlist_name}' on Tidal...")
            try:
                new_playlist_future = session.user.create_playlist(playlist_name, f"Transferred from Spotify")
                target_playlist = session.playlist(new_playlist_future.id)
                tidal_playlists[playlist_name] = target_playlist # Add to our dict
                print("Playlist created successfully.")
            except Exception as e:
                print(f"Error creating playlist '{playlist_name}': {e}")
                continue # Skip to the next playlist

        # 4. Search for songs and collect their Tidal IDs
        song_ids_to_add = []
        for song_name, artist_name in songs:
            print(f"  - Searching for: {song_name} by {artist_name}")
            tidal_song_id = search_tidal_song(song_name, artist_name)
            if tidal_song_id:
                song_ids_to_add.append(tidal_song_id)
        
        # 5. Add collected songs to the target playlist
        if song_ids_to_add:
            print(f"Adding {len(song_ids_to_add)} found songs to '{playlist_name}'...")
            try:
                target_playlist.add(song_ids_to_add)
                print("Songs added successfully!")
            except Exception as e:
                print(f"An error occurred while adding songs to '{playlist_name}': {e}")
        else:
            print(f"No songs were found on Tidal for this playlist.")

if __name__ == "__main__":
    # Find CSV files in the current directory
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and f.startswith('Spotify Bibliothek')]
    
    if not csv_files:
        print("No 'Spotify Bibliothek*.csv' files found in the directory.")
    else:
        print("\nFound the following CSV files to process:")
        for i, f in enumerate(csv_files):
            print(f"  [{i+1}] {f}")

        while True:
            try:
                choice_str = input(f"\nEnter the number of the file to process (1-{len(csv_files)}): ")
                choice = int(choice_str)
                if 1 <= choice <= len(csv_files):
                    selected_file = csv_files[choice - 1]
                    transfer_songs(selected_file)
                    print(f"\n--- Finished processing {selected_file} ---")
                    break
                else:
                    print("Invalid number. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    input("\nPress Enter to exit...")

