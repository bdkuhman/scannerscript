# import threading
# import signal, sys
# import json
# import requests
# import paho.mqtt.client as mqtt

# Originally used when this was running on an rpi.
# This script is now headless...
# def wake_screen():
#     os.system("xset -display :0.0 s reset && xset -display :0.0 dpms force on")


# def off_screen():
#     os.system("xset -display :0.0 s activate && xset -display :0.0 dpms force off")


# def rotate_screen():
#     os.system("DISPLAY=:0 xrandr -o left")


##mqtt stuffs

# Originally implemented to be able to rotate/wake the screen when on a rpi.
# Don't need mqtt things for now...

# topic_name="topic"

# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code " + str(rc))

#     # Subscribing in on_connect() means that if we lose the connection and
#     # reconnect then subscriptions will be renewed.
#     client.subscribe([(topic_name, 1)])


# def on_message(client, userdata, message):
#     print("Message received: " + message.topic + " : " + str(message.payload.decode()))
#     if message.topic == topic_name:
#         msg = message.payload.decode()
#         if msg == "wakeup":
#             wake_screen()
#         elif msg == "off":
#             off_screen()
#         elif msg == "rotate":
#             rotate_screen()
#         # with open('/home/pi/mqtt_update.txt', 'a+') as f:
#         #    f.write("received topic2")


# def mqtt_loop():
#     client.loop_forever()

# TODO: Pass in through env.
# broker_address = ""  # Broker address
# port = 1883  # Broker port
# user = ""  # Connection username
# password = ""  # Connection password


# client = mqtt.Client()  # create new instance
# client.username_pw_set(user, password=password)  # set username and password
# client.on_connect = on_connect  # attach function to callback
# client.on_message = on_message  # attach function to callback

# client.connect(broker_address, port=port)  # connect to broker

# client.loop_forever()