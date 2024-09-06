import spotipy  
import random
import logging
import os
import sys
import sqlite3
from spotipy import SpotifyOAuth
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get("LOG_LEVEL")),
        datefmt='%Y-%m-%d %H:%M:%S')

client_id=os.environ.get("SPOTIPY_CLIENT_ID")
client_secret=os.environ.get("SPOTIPY_CLIENT_SECRET")
redirect_uri=os.environ.get("SPOTIPY_REDIRECT_URI")
scope="user-top-read,user-library-read,user-read-recently-played"

logging.info('Process Start!')

creds = SpotifyOAuth(scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, open_browser=False)
sp = spotipy.Spotify(auth_manager=creds)

music_dir = os.environ.get("MUSIC_DIR")
playlist_dir = os.environ.get("PLAYLIST_DIR")

if not os.path.exists(music_dir):
  os.mkdir(music_dir)
if not os.path.exists(playlist_dir):
  os.mkdir(playlist_dir)

def delete_old_playlists_from_navidrome():
    dbfile =  os.environ.get("NAVIDROME_DB_FILE")
    if os.path.exists(dbfile):
        con = sqlite3.connect(dbfile)
        cur = con.cursor()
        cur.execute("DELETE FROM playlist")
        cur.execute("DELETE FROM playlist_fields")
        con.commit()
        cur.close()
        con.close()

def my_reccommendations():
    try:
        top_tracks = sp.current_user_top_tracks(limit=50, time_range='long_term')
        logging.info('Loaded your custom top tracks')
        liked_tracks = sp.current_user_saved_tracks(limit=50)
        logging.info('Loaded your top liked tracks')
        history = sp.current_user_recently_played(limit=50)
        logging.info('Loaded your played tracks')
        for i in range(int(os.environ.get("NUM_USER_PLAYLISTS"))):
            logging.info('Searching your reccomendations (playlist %s)', str(i+1))
            top_track_ids = [track['id'] for track in top_tracks['items']]
            liked_track_ids = [track['track']['id'] for track in liked_tracks['items']]
            history_track_ids = [track['track']['id'] for track in history['items']]
            seed_track_ids = top_track_ids + liked_track_ids + history_track_ids
            random.shuffle(seed_track_ids)
            results = sp.recommendations(seed_tracks=seed_track_ids[0:5], limit=int(os.environ.get("ITEMS_PER_PLAYLIST")))
            write_reccomandation_file(playlist_dir + "/" + "My Reccomendations - " + str(i+1) + ".m3u", results)
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def get_artist(name):
    results = sp.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        return items[0]
    else:
        return None

def write_reccomandation_file(playlist_path_file, results):
    try:
        reccomendations_array = []
        for track in results['tracks']:
            
            logger.debug('Searching %s - %s in your music library (%s)', track['name'], track['artists'][0]['name'], music_dir)
            artist_path_dir = None
            for artist_name in os.listdir(music_dir):
                if artist_name.lower() ==  track['artists'][0]['name'].lower() or artist_name.lower() in track['artists'][0]['name'].lower() or track['artists'][0]['name'].lower() in artist_name.lower():
                    artist_path_dir = os.path.join(music_dir, artist_name)
                    break
            if artist_path_dir is not None:
                for song_title in os.listdir(artist_path_dir):
                    if not "live" in song_title.lower() and not "acoustic" in song_title.lower():
                        no_extension_title = os.path.splitext(song_title)[0]
                        parsed_song_title = no_extension_title.split("-")[len(no_extension_title.split("-"))-1].strip()
                        if parsed_song_title.lower() in track['name'].lower() or track['name'].lower() in song_title:
                            song_path_file = os.path.join(artist_path_dir, song_title)
                            reccomendations_array.append(song_path_file)
        if os.path.exists(playlist_path_file):
            os.remove(playlist_path_file)
        if len(reccomendations_array) > 0:
            with open(playlist_path_file, 'a') as opened_playlist_file:
                for reccomendation in reccomendations_array:
                    opened_playlist_file.write(reccomendation + '\n')
                    logging.debug('Writing reccomendation %s to playlist (%s)', reccomendation, playlist_path_file)

    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def show_recommendations_for_artist(name):
    logging.info('Searching reccomendations for: %s', name)
    artist = get_artist(name)
    results = sp.recommendations(seed_artists=[artist['id']], limit=int(os.environ.get("ITEMS_PER_PLAYLIST")))
    write_reccomandation_file(playlist_dir + "/" + name + " - Reccomendations.m3u", results)

delete_old_playlists_from_navidrome()

my_reccommendations()

for artist_name in os.listdir(music_dir):
  show_recommendations_for_artist(artist_name)


logging.info('Process Done!')