import sys
import spotipy
import vlc
import time
import spotipy.util as util

scope = 'user-library-read'

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print "Usage: %s username" % (sys.argv[0],)
    sys.exit()
token = util.prompt_for_user_token(username,scope,client_id='107ff4c93c9b4e01a848fbdba04aac5a',client_secret='354cc166e50b4317bb6e3e1a3dee7b32',redirect_uri='https://open.spotify.com/album/5OVcAB06ttNop0LKRUUKKD')

if token:
    sp = spotipy.Spotify(auth=token)
    bpm_input = 130

#method 1 : play particualr song based on input bpm
    if bpm_input == 130:
        features = sp.audio_features('https://open.spotify.com/track/0A9y4c4dkI68IEnsRGtWil')
        print features
        p = vlc.MediaPlayer('https://p.scdn.co/mp3-preview/c01a2e3b83e357cb99b715629ad378319b816eea?cid=107ff4c93c9b4e01a848fbdba04aac5a')
        p.play()
        time.sleep(32)
    else:
        print "No matching bpm track found"
else:
    print "Can't get token for", username
