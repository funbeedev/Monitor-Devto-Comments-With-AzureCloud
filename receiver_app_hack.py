import requests
from bs4 import BeautifulSoup
import pyttsx3
import paho.mqtt.client as mqtt # First run: pip install paho-mqtt
from datetime import datetime
import time

# this will store data received in mqtt callback
data_received = []  # TODO: try not to use globals..


def text_to_speech(text):

    # read text out loud
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

    # engine.say("Hello universe!!")
    # engine.runAndWait()


# Called when client is connected to server
def on_connect(client, userdata, flag, code):
    if code == 0:
        print("MQTT Connected")
    else:
        print("MQTT Failed to Connect")
    print(client, userdata, flag, code)


# Called when message is received on subscribed topic
def on_message(client, data, msg):
    global data_received
    data_received = []

    topic_received = msg.topic
    data_received.append(msg.payload.decode())

    print('\n--------------------------------')
    print('Message received @ Time: %s' %(datetime.now()))
    print("topic: %s" % topic_received)
    print("data: %s" % data_received)

    if (msg.topic == ''):
        None


# Setup mqtt connection
def mqtt_setup(broker, topic_1, topic_2):
    client = mqtt.Client()

    # set callback when connected to broker
    client.on_connect = on_connect

    # set callback when message is received
    client.on_message = on_message

    # connect to broker
    client.connect(broker)

    # subscribe to topic if specified
    client.subscribe([(topic_1, 0), (topic_2, 2)])  # TODO: is there a need to have 0 and 2 different?

    return client


def start_program_flow():

    global data_received
    last_data_received = []

    # setup mqtt conn to broker and topics
    client = mqtt_setup('raspberrypi', 'message', 'none')
    client.loop_start()

    while True:
        time.sleep(3)

        # process if not empty and not same as last data
        if(data_received != [] and last_data_received != data_received):
            last_data_received = data_received
            text_to_speech(data_received)


if __name__ == "__main__":
    print("--------- start receive app ---------")
    start_program_flow()
