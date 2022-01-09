# Zap2-Userside

> OBS: This repository should be used in adition to zap2-serverside

### Introduction

This project aims to simulate one chat application with end-to-end encryption running through a websocket server. For that it was implemented the Double Ratchet Encryption, if you want to read about it I recommend reading [Niko's post](https://nfil.dev/coding/encryption/python/double-ratchet-example/), as well as toying around with the script crypto_tester.py where you can see with more detail the process each messsage goes through.

My initial objectives with this project are:
  |                                                                                             |     |
  | --------------------------------------------------------------------------------------------|-----| 
  | Verify provided data, such as checking if the telephone is valid                            | :x: |
  | Implement the Double Ratchet Encryption                                                     | ✔️ |
  | Generate new keys for new chatrooms as old keys are used                                    | :x: |
  | Establish the connection between two users through the application                          | ✔️ |
  | Implement group chats with encryption                                                       | :x: |
  | Add expiring tokens with something like redis to verify the authenticity of the connection  | :x: |
  | Deal with server connection problems after signup                                           | ✔️ |
  | Identify and solve problems of data continuity without losing the chat security             | ✔️ |
  | Implement a half-decent graphical interface                                                 | ✅ |
  | Implement dockerfile and docker-compose to deploy application                               | :x: |
  | Make the chat server available on a web domain so it can be tested online                   | ✔️ |

After this project becomes robust enough I aim to:
  |                                                                                                                         |     |
  | ------------------------------------------------------------------------------------------------------------------------|-----| 
  | Remove the server-side application making it a P2P application                                                          | :x: |
  | Study the possibility of using algorithms for Self-Balancing networks on the P2P web and it's impact on limiting errors | :x: |

### Running the program
If you are not using the online server it is necessary to deploy the server located on [this repository](https://github.com/caiocaldeira3/zap2-serverside).

#### Manually
First it is necessary to ensure the existence of the folder <i>encrypted_keys</i> on the repository, it's path should be as follow:

├── zap2-userside  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── scripts  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── user  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── util  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <b>encrypted_keys*</b> 

Each cloned repository can act as one singular user. If you want to simulate multiple users chatting, for now, it is necessary to clone as many times as you want users.

Then you should install all python requirements executing:
```
pip install -r requirements.build.txt
pip install -r requirements.txt
```
PS: It is advisable to execute these commands separeted due to the necessity of having the wheel module already installed for the installation of the other modules.  

After that, assuming you are using an appropriated python version, 3.9.7+ should do, to create one session you should traverse to the <i>user</i> folder and run:
```
python run.py
```

With the script running you can communicate with the server using the following commands
  * login
  * logout
  * signup
  * create-chat
  * send-message
  * info

As long as all the devices communicate with the same server you should be able to send message among repositories





