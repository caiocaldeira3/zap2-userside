# Zap2-Userside

> OBS: This repository should be used in adition to zap2-serverside

### Introduction

This project aims to simulate one chat application with end-to-end encryption running through a websocket server. For that it was implemented the Double Ratchet Encryption, if you want to read about it I recommend reading [Niko's post](https://nfil.dev/coding/encryption/python/double-ratchet-example/) as well as toying around with the script crypto_tester.py where you can see with more detail the process each message goes through.

My initial objectives with this project are:
  |                                                                                             |     |
  | --------------------------------------------------------------------------------------------|-----| 
  | Verify provided data, such as checking if the telephone is valid                            | :x: |
  | Implement the Double Ratchet Encryption                                                     | :heavy_check_mark: |
  | Generate new keys for new chatrooms as old keys are used                                    | :x: |
  | Establish the connection between two users through the application                          | :heavy_check_mark: |
  | Implement group chats with encryption                                                       | :x: |
  | Add expiring tokens with something like redis to verify the authenticity of the connection  | :x: |
  | Deal with server connection problems after signup                                           | :x: |
  | Identify and solve problems of data continuity without losing the chat security             | :x: |
  | Implement a half-decent graphical interface                                                 | :white_check_mark: |
  | Make the chat server available on a web domain so it can be tested online                   | :x: |

After this project becomes robust enough I aim to:
  |                                                                                                                         |     |
  | ------------------------------------------------------------------------------------------------------------------------|-----| 
  | Remove the server-side application making it a P2P application                                                          | :x: |
  | Study the possibility of using algorithms for Self-Balancing networks on the P2P web and it's impact on limiting errors | :x: |

### Running the program
Firstly it's necessary to have the zap2-serverside running on your localhost or web domain that your have configured. For that you should follow the instructions on [this repository](https://github.com/caiocaldeira3/zap2-serverside).

Since the best way I found to storage the keys used in the encryption process was to save them locally on the repository folder, this repository is equivalent as one user. If you want to simulate multiple users chatting, for now, it is advised to clone as many times as you want users. This also mean it might be necessary to ensure that you have the folder, creating it, if necessary:

├── zap2-userside  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── scripts  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── user  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── util  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <b>encrypted_keys*</b>  

To create one session simply run `python run.py` on the user folder, inside the repository, and experiment with the commands available:
  * login
  * logout
  * signup
  * create-chat
  * send-message
  * <del>info</del>  
 
As long as all the <i>devices</i> communicate with the same server you should be able to send message among repositories.  





