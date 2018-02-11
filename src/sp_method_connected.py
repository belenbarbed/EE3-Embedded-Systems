import sys
import spotipy
import vlc
import time
import spotipy.util as util
import urllib


def play_music(input_bpm):

    scope = 'user-library-read'
    #Note username = 21s5p2g6odn7smk6ytcfz5m3q
    username = '21s5p2g6odn7smk6ytcfz5m3q'
    #if len(sys.argv) > 1:
    #    username = sys.argv[1]
    #else:
    #    print "Usage: %s username" % (sys.argv[0],)
    #    sys.exit()
    token = util.prompt_for_user_token(username,scope,client_id='107ff4c93c9b4e01a848fbdba04aac5a',client_secret='354cc166e50b4317bb6e3e1a3dee7b32',redirect_uri='https://open.spotify.com/album/5OVcAB06ttNop0LKRUUKKD')

    if token:
        sp = spotipy.Spotify(auth=token)

        #input_bpm from sensor
        #input_bpm = 130.0

    #method 2 : make playlist name=bpm_input then play tracks from that playlist


        #Go to user's Favorite Running Songs with different input_bpm
        results = sp.user_playlist(username, playlist_id = 'https://open.spotify.com/user/21s5p2g6odn7smk6ytcfz5m3q/playlist/0cZgYMWfSFpOfhmCmggaIj',fields="tracks")
        tracks = results['tracks']

        #Go through the list of songs in the mentioned playlist
        for i, item in enumerate(tracks['items']):
            track = item['track']
            print "   %d %32.32s %s" % (i, track['artists'][0]['name'],
                track['name'])
                # track['preview_url'], track['uri'])

            #getting url for audio_features() argument
            url = 'https://open.spotify.com/track/'
            uri = track['uri']
            getVars = {uri[14 : 36] :''}
            final_uri = url + urllib.urlencode(getVars)
            final_url = final_uri[0:53];
            #print final_url[0:53]

            #get track audio_features, then extract tempo
            features = sp.audio_features(final_url[0 : 53])
            #print features
            feature_vals = features[0].values()
            tempo =  feature_vals[4]
            print("tempo is "+str(tempo))

            #for example, if tempo is 130 (play any songs > 125bpm and <135bpm)
            if tempo > input_bpm - 5  and  tempo < input_bpm + 5:
                print "and your Running Tempo is "
                print input_bpm
                print "Your Music Tempo is "
                print tempo
                #print track['preview_url']
                p = vlc.MediaPlayer(track['preview_url'])
                p.play()
                time.sleep(31)

    else:
        print "Can't get token for", username
