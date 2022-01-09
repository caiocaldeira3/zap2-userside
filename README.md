# Zap2-Serverside

> OBS: This repository should be used in adition to zap2-userside

### Introduction

This project aims to simulate one chat application with end-to-end encryption running through a websocket server. For that it was implemented the Double Ratchet Encryption, if you want to read about it I recommend reading [Niko's post](https://nfil.dev/coding/encryption/python/double-ratchet-example/).

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
  | Implement dockerfile and docker-compose to deploy application                               | ✔️ |
  | Make the chat server available on a web domain so it can be tested online                   | ✔️ |

After this project becomes robust enough I aim to:
  |                                                                                                                         |     |
  | ------------------------------------------------------------------------------------------------------------------------|-----| 
  | Remove the server-side application making it a P2P application                                                          | :x: |
  | Study the possibility of using algorithms for Self-Balancing networks on the P2P web and it's impact on limiting errors | :x: |

### Running the program
It is recommended to deploy the server using the docker-compose tool, but it is possible to deploy it manually, on your localhost. 

#### Using docker-compose (Recommended)
On the repository's root folder execute:  
```
docker-compose up -d
```

#### Manually
To deploy the server manually it is necessary to install all python requirements executing:
```
pip install -r requirements.build.txt
pip install -r requirements.txt
```
PS: It is advisable to execute these commands separeted due to the necessity of having the wheel module already installed for the installation of the other modules.  

After that, assuming you are using an appropriated python version, 3.9.7+ should do, you should traverse to the <i>server</i> folder and run:
```
python run.py
```
With that the server should be up and running.

Then to simulate users using the server you should read the instructions on [this repository](https://github.com/caiocaldeira3/zap2-userside).





