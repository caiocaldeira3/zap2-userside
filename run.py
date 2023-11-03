from gevent import monkey

_ = monkey.patch_all()

from app import api
from app.services import user as ussr

action = ""
while action != "exit":
    if action == "login":
        api.login()

    elif action == "logout":
        api.logout()

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

    elif action == "info":
        try:
            print(f"user_id: {api.user_id}")
            user = ussr.find_with_id(api.user_id)
            print(f"user-name: {user.name} | user-phone: {user.telephone}")

        except Exception as exc:
            print("user not logged in")

    else:
        print("Available actions:")
        print("login | logout | signup | create-chat | send-message | info")

    action = input("action: ")

api.logout()