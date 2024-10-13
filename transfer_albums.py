import tidalapi
import os
import csv
import re

session1 = tidalapi.Session()
print('Enter your credentials for the account you want to transfer from')
session1.login_oauth_simple()
uid1 = session1.user.id
TidalUser1 = tidalapi.Favorites(session1, uid1)
albums = TidalUser1.albums()


def search_tidal_song(song_name, artist_name):
    song_name = re.sub(r'\s*\(.*?\)', '', song_name) #removes any parenthesis and words within because more accurate search on tidal
    query = song_name + " " + artist_name
    query_length = len(song_name)
    results = session1.search(query=query, limit=5,) #searches tidal with the query and gets top 5 results
    if len(results['tracks']) > 0:
        # Get the first result as the closest match
        min_length = 1000
        min_index = 0
        for i in range(len(results['tracks'])):

            if song_name == results['tracks'][i].name and artist_name == results['tracks'][i].artist.name: #if song name and artist exactly the same on tidal
                min_index = i
                break
            
            #this section here I added because I kept getting remixes of songs when song was not a remix and vice versa
            song_remix = song_name.lower().find('remix')
            result_remix = results['tracks'][i].name.lower().find('remix')
            requirement_met = False
            if (song_remix == -1 and result_remix == -1) or (song_remix != -1 and result_remix != -1):
                requirement_met = True

            #if the song name is even in the result (note you can remove that part of the if statement if you're not getting adequate results and see if you get better)
            if results['tracks'][i].name.find(song_name) != -1 and requirement_met:
                length_track = len(results['tracks'][i].name)
                diff = abs(query_length - length_track)
                #gets the least difference in length of the song name
                if diff < min_length:
                    min_index = i
                    min_length = diff

        for i in range(len(results['tracks'])):
            if min_index != i:
                if results['tracks'][i].name == results['tracks'][min_index].name and results['tracks'][i].artist.name == results['tracks'][min_index].artist.name:
                    results['tracks'][i].explicit

                
        track = results['tracks'][min_index]
        #look at log.txt for the tidal song found and if song not found
        #look at log2.txt for song differences in names and artists
        with open(r'YOUR PATH\log.txt', 'a', encoding='utf-8') as f:
            f.write(f"Tidal Song ID: {track.id}, Name: {track.name}, Artist: {track.artist.name}")
            f.write('\n')
        if song_name != track.name:
            with open(r'YOUR PATH\log2.txt', 'a', encoding='utf-8') as f:
                f.write(f"NAME:      Tidal Song ID: {track.id}, Name: {track.name}, Artist: {track.artist.name}, ||||||| Spotify: {song_name}, {artist_name}")
                f.write('\n')
        elif artist_name != track.artist.name:
            with open(r'YOUR PATH\log2.txt', 'a', encoding='utf-8') as f:
                f.write(f"ARTIST:      Tidal Song ID: {track.id}, Name: {track.name}, Artist: {track.artist.name}, |||||| Spotify: {song_name}, {artist_name}")
                f.write('\n')
        return track.id
    else: #did not find song based on query
        with open(r'YOUR PATH\log.txt', 'a', encoding='utf-8') as f:
            f.write(f"No results found for {song_name} by {artist_name}")
            f.write('\n')
        print(f"No results found for {song_name} by {artist_name}")
        return None

ids = []

# Read your CSV file
with open(r'YOUR PATH\songs.csv', newline='\n', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        spotify_id = row[0]
        song_name = row[1]
        artist_name = row[2]
        
        # print(f"Searching for: {song_name} by {artist_name}")
        tidal_song_id = search_tidal_song(song_name, artist_name)
        ids.append(tidal_song_id)

uid1 = session1.user.id

print('Adding ...')
for id in ids:
    try:
        playlists = TidalUser1.playlists()
        for playlist in playlists:
            if playlist.name == 'NAME OF YOUR PLAYLIST THAT YOU WANT TO ADD THE SONGS TO':
                found_playlist = session1.playlist(playlist.id)
                break

        found_playlist.add([id])
    except Exception as e:
        print(f"An error occurred while adding id {id}: {e}")

os.system("pause")
