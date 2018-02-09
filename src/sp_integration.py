import sys
import spotipy
import vlc
import time
import spotipy.util as util

scope = 'user-library-read'

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()
token = util.prompt_for_user_token(username,scope,client_id='107ff4c93c9b4e01a848fbdba04aac5a',client_secret='354cc166e50b4317bb6e3e1a3dee7b32',redirect_uri='https://open.spotify.com/album/5OVcAB06ttNop0LKRUUKKD')

if token:
    lz_uri = 'spotify:artist:36QJpDe2go2KgaRleHCDTp'

    sp = spotipy.Spotify(auth=token)
    results = sp.artist_top_tracks('https://open.spotify.com/artist/6PXS4YHDkKvl1wkIl4V8DL', country='US')

    for track in results['tracks'][:10]:
        print('track    : ' + track['name'])
        print('audio    : ' + track['preview_url'])
        print('cover art: ' + track['album']['images'][0]['url'])
        p = vlc.MediaPlayer(track['preview_url'])
        p.play()
        time.sleep(32)
        print
else:
    print ("Can't get token for", username)
