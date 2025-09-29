import tidalapi
import os
import csv
import re

# TuneMyMusic Spotify->CSV file path
lib = r'{YOUR_CSV_PATH}\My Spotify Library.csv'
# desired log path
log_path = 'YOUR_LOG_PATH'

session = tidalapi.Session()
print('Enter your credentials for the account you want to transfer from')
session.login_oauth_simple()


def search_tidal_song(song_name, artist_name):
    song_name = re.sub(r'\s*\(.*?\)', '', song_name) # removes any parenthesis and words within because more accurate search on tidal
    query = song_name + " " + artist_name
    query_length = len(song_name)
    results = session.search(query=query, models=[tidalapi.media.Track], limit=5,) #searches tidal with the query and gets top 5 results
    if len(results['tracks']) > 0:
        # Get the first result as the closest match
        min_length = 1000
        min_index = 0
        for i in range(len(results['tracks'])):

            if song_name == results['tracks'][i].name and artist_name == results['tracks'][i].artist.name: #if song name and artist exactly the same on tidal
                min_index = i
                break
            
            # this section here I added because I kept getting remixes of songs when song was not a remix and vice versa
            song_remix = song_name.lower().find('remix')
            result_remix = results['tracks'][i].name.lower().find('remix')
            requirement_met = False
            if (song_remix == -1 and result_remix == -1) or (song_remix != -1 and result_remix != -1):
                requirement_met = True

            # if the song name is even in the result (note you can remove that part of the if statement if you're not getting adequate results and see if you get better)
            if results['tracks'][i].name.find(song_name) != -1 and requirement_met:
                length_track = len(results['tracks'][i].name)
                diff = abs(query_length - length_track)
                # gets the least difference in length of the song name
                if diff < min_length:
                    min_index = i
                    min_length = diff

        for i in range(len(results['tracks'])):
            if min_index != i:
                if results['tracks'][i].name == results['tracks'][min_index].name and results['tracks'][i].artist.name == results['tracks'][min_index].artist.name:
                    results['tracks'][i].explicit

                
        track = results['tracks'][min_index]
        with open(r"{log_path}\pylogs\log_found.txt", 'a', encoding='utf-8') as f:
            f.write(f"Tidal Song ID: {track.id}, Name: {track.name}, Artist: {track.artist.name}")
            f.write('\n')
        if song_name != track.name:
            with open(r"{log_path}\pylogs\log_diff.txt", 'a', encoding='utf-8') as f:
                f.write(f"NAME:      Tidal Song ID: {track.id}, Name: {track.name}, Artist: {track.artist.name}, ||||||| Spotify: {song_name}, {artist_name}")
                f.write('\n')
        elif artist_name != track.artist.name:
            with open(r"{log_path}\pylogs\log_diff.txt", 'a', encoding='utf-8') as f:
                f.write(f"ARTIST:      Tidal Song ID: {track.id}, Name: {track.name}, Artist: {track.artist.name}, |||||| Spotify: {song_name}, {artist_name}")
                f.write('\n')
        return track.id
    else: # did not find song based on query
        with open(r"{log_path}\pylogs\log_not_found.csv", 'a', encoding='utf-8') as f:
            f.write(f'"{song_name}","{artist_name}"')
            f.write('\n')
        print(f"No results found for {song_name} by {artist_name}")
        return None


# batch iterable
def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


# Read your CSV file
with open(lib, newline='\n', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    # Skip the header row
    next(reader)

    playlist_hash = {}

    for row in reader:
        song_name = row[0]
        artist_name = row[1]
        playlist_name = row[3]

        # group by playlist name in hash
        if playlist_name not in playlist_hash:
            playlist_hash[playlist_name] = []

        tidal_song_id = search_tidal_song(song_name, artist_name)
        if tidal_song_id:
            playlist_hash[playlist_name].append(tidal_song_id)

    print('Adding ...')


try:
    # iterate over each playlist and create it in tidal. Liked Songs will be named "Favorite Songs" if you use TuneMyMusic
    for playlist_name in playlist_hash:
        playlist = session.user.create_playlist(playlist_name, "Imported from Spotify")
        # the api has a limit of 1000, so we batch the ids to avoid problems
        for batch_ids in batch(playlist_hash[playlist_name], 1000):
            playlist.add(batch_ids)
except Exception as e:
    with open(r"{log_path}\pylogs\log_exception.txt", 'a', encoding='utf-8') as f:
        f.write(f"An error occurred while adding: {e}")
        f.write('\n')
    print(f"An error occurred while adding: {e}")


os.system("pause")

