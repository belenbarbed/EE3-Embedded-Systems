import paho.mqtt.client as mqtt
import ast
import sp_method_connected

isFirst = True

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("esys/The100/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    #print(msg.topic+" "+str(msg.payload))
    #print(str(msg.payload))
    global isFirst

    if(isFirst == False):
        d = ast.literal_eval(msg.payload)
        bpm = float(d['bpm'])
        print(bpm)
        sp_method_connected.play_music(bpm)
    isFirst = False

client = mqtt.Client("TrackIt")
client.on_connect = on_connect
client.on_message = on_message

#client.connect("192.168.0.10", 1883, 60)
client.connect("iot.eclipse.org", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
print("Hello world")
