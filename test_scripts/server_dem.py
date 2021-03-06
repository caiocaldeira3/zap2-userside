import sys
import time

from pathlib import Path

app_path = Path(__file__).parent.parent

sys.path.append(str(app_path))

from app.models.chat import Chat

from app import api

other_phone = sys.argv[2] if len(sys.argv) == 3 else "bub"
chat_name = sys.argv[1] if len(sys.argv) >= 2 else "server"
print(f"other phone is: {other_phone}\n")

print("wait for authentication")
api.login()
time.sleep(15)
print()

print("create chat")
api.create_chat(chat_name, [ other_phone ])
time.sleep(5)
print()

chat = Chat.query.filter_by(name=chat_name).one()
print(chat.id)
print("sending messages")
api.send_message(chat.id, "oi bob", debug=True)

time.sleep(3)
print()

print("receive message")
time.sleep(5)
print()

print("sending message")
api.send_message(chat.id, "te odeio bob", debug=True)
time.sleep(5)
print()

print("sending message")
api.send_message(chat.id, "brinks", debug=True)
time.sleep(5)
print()

time.sleep(5)
api.logout()