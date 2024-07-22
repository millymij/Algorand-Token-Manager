## Algorand Token Manager
System to generate and validate Algorand tokens authorising blockchain transactions.
The system is set to both dispatch and receive tokens via SMS text.
The main system's components are:

### 'core.py' 
Main script managing interactions with the blockchain (i.e. account generation, transaction construction) and Logic Signature handling (i.e. Creation, Encoding and Decoding of Logic Signatures).

### 'sms_utils.py'
Manages interaction with the Vonage SMS API and methods to Send/Recieve messages. 

### 'server.py'
Routes requests from the UI to the backend.




## Requirements

- Python 3.6+
- Docker (to run a local Algorand node) 4.26.0
- Flask (installation via pip) 3.0.3
- Vonage Python SDK 3.13.0
- Algorand Python SDK 2.5.0
- pytest, unittest  (installation via pip) 8.1.1
- Requests, Responses  (installation via pip) 1.12.1
- Ngrok 3.5.0




## Setup:

### Docker Version 4.26.0
Install Docker Compose from: https://docs.docker.com/compose/install/

### Algorand Node Version 4.26.0
Install and setup sandbox from Algorand repo: https://github.com/algorand/sandbox
Version 4.26.0

### Vonage API Version 3.13.0
Create an account with Vonage API at https://www.vonage.co.uk/unified-communications and save its credentials (secret and key) in environment variables.
Then, install Vonage Python SDK at https://github.com/Vonage/vonage-python-sdk

### Ngrok Version 3.5.0
To run ngrok on port 3000, from CLI: ngrok http 3000




## External Libraries:

### Standard Python Libraries 

### ('hashlib', 'json', 'base64', 'ast' )
Data encoding and cryptographic operations.

### ('json')
Managing of JSON data when handling HTTP requests.

### ('multiprocessing.Process')
Handling parallel tasks execution.


### Algorand SDK ('algosdk')
Algorand SDK GitHub Repository at (https://github.com/algorand/py-algorand-sdk), MIT Licence.
Used for interacting with the Algorand blockchain.


### Logging Library ('logging')
Used to log events.


### Vonage Python SDK ('vonage')
Enables SMS messaging functionalities to interact with the Vonage API through the Python application.


### Flask and Werkzeug
Framework to create lightweight web applications. Used to create a webserver managing UI and SMS HTTP requests.
More about Flask in documentation at: https://flask.palletsprojects.com/en/3.0.x/


### Testing Libraries: 

### 'unittest', 'pytest'
Testing libraries uses for unit testing and integration testing respectively. When running integration tests with pytest, server.py needs to be running. To run the integration tests, in another terminal window type: pytest -vv

### 'response', 'request'
Handling of HTTP requests and responses to simulate network interaction during testing.



## Setup for receiving SMS
To receive an SMS text, create a webhook for SMS delivery and make the webhook's url publicly available.
This is achieved with a tool like Ngrok; once Ngrok is installed, from the terminal write: ngrok http 3000
Then, copy the forwarding link (for example : https://734e-2a02-c7c-d176-6d00-c816-307d-d032-3b83.ngrok-free.app)

We also need to create an account with the Vonage API and purchase a virtual phone number, which the user will send messages to to communicate with the system.
From the Vonage dashboard, click 'Create Application'. In the Capabilities section, select Messages and input your webhook frowarding URL for both Inbound and Status URL. For the 'Inbound URL' field, append '/webhooks/inbound' at the end of the link, like this:
https://734e-2a02-c7c-d176-6d00-c816-307d-d032-3b83.ngrok-free.app/webhooks/inbound

while for the 'Status URL' field append '/webhooks/status'.
for example: https://734e-2a02-c7c-d176-6d00-c816-307d-d032-3b83.ngrok-free.app/webhooks/status

Click on 'Generate New Application' and click to the button below 'Link' to link the application to the virtual phone number purchased. Now, if a user sends an SMS to the virtual phone number we purchased, it will be forwarded to the Vonage API that will in turn send it to our Ngrok client.

Note: unless purchasing a subscription with Ngrok, the Ngrok forwarding link expires after 60 minutes. After that, you will need to execute again the above procedure for receiving messages, for a new link.