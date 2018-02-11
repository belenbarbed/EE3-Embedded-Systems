import sys
import spotipy
import vlc
import time
import spotipy.util as util

scope = 'user-library-read'

def show_tracks(tracks):
    for i, item in enumerate(tracks['items']):
        track = item['track']
        print "   %d %32.32s %s %s" % (i, track['artists'][0]['name'],
            track['name'], track['preview_url'])

        p = vlc.MediaPlayer(track['preview_url'])
        p.play()
        time.sleep(32)

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print "Usage: %s username" % (sys.argv[0],)
    sys.exit()
token = util.prompt_for_user_token(username,scope,client_id='107ff4c93c9b4e01a848fbdba04aac5a',client_secret='354cc166e50b4317bb6e3e1a3dee7b32',redirect_uri='https://open.spotify.com/album/5OVcAB06ttNop0LKRUUKKD')

if token:
    sp = spotipy.Spotify(auth=token)
    #input_bpm from sensor
    input_bpm = 150

#method 2 : make playlist on spotify then when playlist_name=bpm_input, play tracks from that playlist

    #number of playlists I want to extract from the user
    set_limit = 5;
    #gives me all x number of user's playlists
    results = sp.current_user_playlists(limit=set_limit, offset=0)
    #gives me the values of the keys: [u'items', u'next', u'href', u'limit', u'offset', u'total', u'previous'] of the dict
    result_values = results.values()
    #gives me the values under the key items
    items = result_values[0]
    #gives me the items due to indexing
    playlist_names =[]
    playlist_urls = []
    playlist_ids =[]
    for i in range(0, set_limit):
        #index item from 'items' values
        item_indexed = items[i]
        #indexing the name from particualar item from 'items' values
        playlist_names.append(item_indexed['name'])
        #get playlist_id
        playlist_urls.append(str(item_indexed['external_urls']))

    #enumerate playlist_urls and remove extra characters and extra required url and put in playlist_ids list
    for i, p_id in enumerate(playlist_urls):
        playlist_ids.append(p_id[15:102])

    print "Playlist that will be used to make funky running tunes"
    print playlist_names

    #create dictionary mapping playlist naems with their respective ids
    myPlaylistDict = zip(playlist_names,playlist_ids)

    #iterate the dictionary checking if the input_bpm=playlist_name and if so go to its respective location i.e. playlist_id=playlist_urls
    for key, val in myPlaylistDict:
        if(str(input_bpm) == key):
            results = sp.user_playlist(username, playlist_id = val, fields="tracks")
            tracks = results['tracks']
            print "Playlist Playing Name=" + key
            print "                  "
            print "Input BPM="     + str(input_bpm)
            print "

            #play tracks in playlist...Booyahh!             "
            show_tracks(tracks)



else:
    print "Can't get token for", username
