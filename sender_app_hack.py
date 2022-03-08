from configparser import ConfigParser
import requests
from bs4 import BeautifulSoup
import pyttsx3
import paho.mqtt.client as mqtt # First run: pip install paho-mqtt
from datetime import datetime
import time
import json

# TODO: dont use globals

config_file = 'config_cloud.ini'

# config file contains user settings
config = ConfigParser()
config.read(config_file)

# get all settings from config file
conn_type = config.get('config_cloud', 'conn_type')
mqtt_broker = config.get('config_cloud', 'mqtt_broker')
sub_topic_1 = config.get('config_cloud', 'sub_topic_1')
sub_topic_2 = config.get('config_cloud', 'sub_topic_2')
pub_topic_1 = config.get('config_cloud', 'pub_topic_1')

print(f'conn_type: {conn_type} | broker: {mqtt_broker}  | sub_topic_1: {sub_topic_1} | sub_topic_2: {sub_topic_2} | pub_topic_1: {pub_topic_1}')


def dev_api_request():
    

    # use dummy json from file for testing
    with open('json.json') as f:
        response_json = json.load(f)

    print(f"number of fields in json / comment blocks: {len(response_json)}")
    print(f"number of keys in each dict: {len(response_json[0])}")

    # list to store everyone who commented
    commenters_usernames = []
    # list to store each comment
    commenters_comments = []

    # loop over each comment block represented as json (a list of dicts)
    for x in range(len(response_json)):
        # extract username from highest level comment block
        print(response_json[x]['user']['username'])
        commenters_usernames.append(response_json[x]['user']['username'])
        commenters_comments.append(response_json[x]['body_html'])

        # start scan for sub comment blocks - represented by 'children' key
        dict_data = response_json[x]
        # while there is data in the dict
        while (dict_data):
            for key in dict_data:
                if(key == 'children'):
                    # if list is empty, set to empty dict to allow exit
                    if(len(dict_data[key]) == 0):
                        dict_data = ''
                    else:
                        # if children list has content, loop through (although len is always 1) and extract username
                        for x in range(len(dict_data[key])):
                            dict_data = dict_data[key][x]
                            print(dict_data['user']['username'])
                            commenters_usernames.append(dict_data['user']['username'])
                            commenters_comments.append(dict_data['body_html'])

    print(f"\nTotal comments: {len(commenters_usernames)}\n")
    return(commenters_usernames, commenters_comments)



def html_to_text(commenters_usernames, commenters_comments):

    # to hold text only version of comments
    commenters_comments_text = []

    # converts the html formatted content to text
    for x in range(len(commenters_comments)):
        # raw_html = BeautifulSoup(commenters_comments[x], features='lxml')
        raw_html = BeautifulSoup(commenters_comments[x])
        # print(raw_html.get_text())
        commenters_comments_text.append(raw_html.get_text())

    # print each comment
    # print(*commenters_comments_text, sep='-------\n')
    for x, y in enumerate(commenters_comments_text):#
        print(x+1)
        print(y)
        
    return commenters_comments_text


def text_to_speech(text):
    
    # read text out loud
    engine = pyttsx3.init()
    engine.say("Start sender app!")
    engine.runAndWait()
    
    # engine.say(text)
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

    topic_received = msg.topic
    data_received = msg.payload

    print('\n--------------------------------')
    print('Time: %s' %(datetime.now()))
    print("Message received")
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


def send_iothub_to_device():
    print("Sending directly from IoTHub to Device")


def run_mqtt_messaging(commenters_usernames, commenters_comments_text):
    # setup mqtt conn to broker and topics
    client = mqtt_setup(mqtt_broker, sub_topic_1, sub_topic_2)

    # commenters_comments_text = '123456789'  # dummy

    while True:
        time.sleep(3)

        # -> send just one piece of data at a time
        x = len(commenters_comments_text) - 1 # last comment in post list
        x = 0  # first comment

        # build up msg to publish
        msg_publish = " username: " + commenters_usernames[x] + " ," + " comment: " + commenters_comments_text[x]
        print(f"Publish latest comment: {msg_publish}")

        # publish to topic
        client.publish(pub_topic_1, msg_publish)

        # -> sending a burst of data at once
        # for x in range(len(commenters_usernames)):
        #     # build up msg to publish
        #     msg_publish = str(x+1) + " username: " + commenters_usernames[x] + " comment: " + commenters_comments_text[x]
        #     # publish to topic
        #     client.publish(publish_topic, msg_publish)

        # also send message via sdk if stated
        if(conn_type == 'c2d'):
            send_iothub_to_device()

        # refresh dev api call to get latest comments
        print("--- REFRESH API ---")
        commenters_usernames, commenters_comments = dev_api_request()
        commenters_comments_text = html_to_text(commenters_usernames, commenters_comments)


def start_program_flow():

    commenters_usernames, commenters_comments = dev_api_request()
    commenters_comments_text = html_to_text(commenters_usernames, commenters_comments)
    text_to_speech(commenters_comments_text)
    run_mqtt_messaging(commenters_usernames, commenters_comments_text)


if __name__ == "__main__":
    print("--------- start sender app ---------")
    start_program_flow()
