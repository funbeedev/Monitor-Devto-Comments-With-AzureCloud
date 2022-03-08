from configparser import ConfigParser
from email import message
from pickle import NONE
import requests
from bs4 import BeautifulSoup
import pyttsx3
import paho.mqtt.client as mqtt # First run: pip install paho-mqtt
from datetime import datetime
import time
import os
import asyncio
import uuid
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message

try:
    # setup gpio if this is a pi
    from gpiozero import LED
    led = LED("GPIO23")
except:
    None

print("\n--------- start device app ---------\n")

# TODO: try not to use globals..

# this will store data received in callbacks
data_received = []  
cloud_data_received = []

# hold number of total msgs received from azure
azure_msgs_count = 0

# def setup_config_ini():

config_file = 'config_device.ini'

# config file contains user settings
config = ConfigParser()
config.read(config_file)

# get all settings from config file
conn_type = config.get('config_device', 'conn_type')
azure_device_conn_string = config.get('config_device', 'azure_device_conn_string')
is_pi = config.get('config_device', 'is_pi')
mqtt_broker = config.get('config_device', 'mqtt_broker')
sub_topic_1 = config.get('config_device', 'sub_topic_1')
sub_topic_2 = config.get('config_device', 'sub_topic_2')
pub_topic_1 = config.get('config_device', 'pub_topic_1')


# print(f'conn_type: {conn_type} | is_pi: {is_pi} | broker: {mqtt_broker}  | sub_topic_1: {sub_topic_1} | sub_topic_2: {sub_topic_2} | pub_topic_1: {pub_topic_1}')
# print(f'Azure string: {azure_device_conn_string}')


def text_to_speech(text):

    # read text out loud
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


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


def azure_message_handler(message):
    global azure_msgs_count
    global cloud_data_received
    global data_received

    azure_msgs_count += 1
    print("\nMessage received from Cloud:")

    # print data from both system and application (custom) properties
    for property in vars(message).items():
        print ("    {}".format(property))

    cloud_data_received = message.data.decode()
    # if not using mqtt then overwrite var used to hold what would have been sent over mqtt
    if(conn_type != 'mqtt'):
        data_received = message.data.decode()

    print(f"Data only: {cloud_data_received}")
    print("Total calls received: {}".format(azure_msgs_count))


def receive_from_azure(azure_client):

    print("Setup Azure Message Handler")
    azure_client.on_message_received = azure_message_handler   
    print("Waiting for Cloud Messages...")


async def send_to_azure(device_client, msg):

    # Connect the device client
    await device_client.connect()
    print(str(datetime.now()) + " | Async connection established to Azure IOT")

    if(msg == 'default'):
        # Send a single message
        print(str(datetime.now()) + " | Sending message to Azure IOT Hub")
        msg = Message(str(datetime.now()) + " | Hello Azure. Device App Started")
        # msg.message_id = uuid.uuid4()
        # msg.content_encoding = "utf-8"
        # msg.content_type = "application/json"
    else:
        msg = Message(str(datetime.now()) + " |" + msg[0])

    await device_client.send_message(msg)
    print(f"\nSending Device -> Cloud:\n {msg}")


def run_blink_led(state):

    if(is_pi == 'yes'):
        if(state == 'ON'):
            print("New Comment. Blink LED on pi!!!!")
            led.on()
        else:
            led.off()
    else:
        print("New Comment. But device has no LED to blink...")


def start_program_flow():

    # to hold messages received
    global data_received
    last_data_received = []

    if(conn_type == 'mqtt'):
        # setup mqtt conn to broker and topics
        mqtt_client = mqtt_setup(mqtt_broker, sub_topic_1, sub_topic_2)
        mqtt_client.loop_start()

    # create instance of the device client using azure connection string
    azure_client = IoTHubDeviceClient.create_from_connection_string(azure_device_conn_string)

    # setup to receive messages from azure
    receive_from_azure(azure_client)

    # send message to azure
    asyncio.run(send_to_azure(azure_client, msg='default'))

    while True:
        time.sleep(3)

        # process if not data is empty and if not same as last data
        if(data_received != [] and last_data_received != data_received):
            last_data_received = data_received

            run_blink_led('ON')  # blink LED
            text_to_speech(data_received)  # read out text
            run_blink_led('OFF')

            # send message received back to azure
            # asyncio.run(send_to_azure(azure_client, data_received))
        

if __name__ == "__main__":
    start_program_flow()
