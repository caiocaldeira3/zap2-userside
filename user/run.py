from app import api

action = ""
while action != "exit":
    if action == "login":
        api.login()
        api.ping()

    elif action == "logout":
        api.disconnect()

    elif action == "signup":
        name = input("username: ")
        phone = input("telephone: ")
        password = input("password: ")

        api.signup(name, phone, password)

    elif action == "create-chat":
        name = input("chatname: ")
        user_phone = input("target user phone: ")

        api.create_chat(name, [ user_phone ])

    elif action == "send-message":
        chat_id = input("chat_id: ")
        message = input("message: ")

        api.send_message(chat_id, message)

    else:
        print("Available actions:")
        print("login | logout | signup | create-chat | send-message")

    action = input("action: ")

api.logout()