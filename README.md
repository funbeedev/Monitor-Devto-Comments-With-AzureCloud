# Monitor-Devto-Comments-With-AzureCloud
Be alerted of new comments on a [DEV.to](https://dev.to) article using the Azure Cloud ☁️

## About
Consists of an application running on the Azure Cloud and another on a device to detect new messages posted on a DEV.to article and alert you by reading out the comment. If the device is a PI, LED will indicate new comments.

- Use the Azure Cloud to alert you when a new comment is posted on your DEV.to post by polling the DEV.to api.
- When a new comment is detected the Azure Cloud will send a message to a selected device registered on the Azure IoT Hub. This message will contain the username along with the comment. The device reads out the username and comment using a text to speech engine.
- As a bonus if the device is a raspberry PI an LED will blink while the comment is being read.
- The method of sending messages from the Azure Cloud to IoT Hub device is through functions provided by the Python Azure IoT Hub SDK. 
- The application is able to route messages using MQTT (Message Queuing Telemetry Transport) if this option is configured in the ini file of apps setup.

## Core technologies and kits overview
✔️ [DEV.to API](https://developers.forem.com/api).  
✔️ Azure Linux Virtual Machines.  
✔️ Azure IoT Hub.  
✔️ Python Requests Module.  
✔️ Python Text to Speech Engine.  
✔️ Raspberry PI.  

If using MQTT:  
✔️ Mosquitto MQTT broker.    
✔️ Paho MQTT.  

## Environment Installations & Setup

### Azure Cloud
- Python pip3 - `sudo apt-get install python3-pip` 
- Python Requests Module - `pip install requests`
- Beautiful Soup - `pip install bs4`
- Python Azure IoT Hub library - `pip install azure-iot-hub`
- Python text-to-speech - `sudo apt-get install espeak` `pip3 install pyttsx3`
- Paho MQTT - `pip install paho-mqtt.`
- Configure the Cloud .ini file

### Device 
- Python Azure IoT Hub SDK - `pip install azure-iot-device`
- Python text-to-speech - `sudo apt-get install espeak` `pip3 install pyttsx3`
- gpiozero (for GPIO control if device is a raspberry pi ) - `sudo apt install python-gpiozero`
- Paho MQTT - `pip install paho-mqtt.`
- Configure the device .ini file

### Tools that helped with development:
- Azure explorer - https://github.com/Azure/azure-iot-explorer/releases
- Azure CLI - https://docs.microsoft.com/en-us/cli/azure/


## Plans for future
- Use better robot voice
- AI processing of comments
- Do more cool stuff with PI interaction
