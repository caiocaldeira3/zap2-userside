import json
import queue
import asyncio
import threading

import dataclasses as dc
import tkinter as tk

from app import api
from app.models.chat import Chat
from app.models.user import User
from app.models.message import Message

from app.util.json_encoder import AlchemyEncoder

@dc.dataclass(init=True, repr=False)
class ZapChat:

    nick: str = dc.field(init=True)

    TEXT_COLOR: str = dc.field(init=True, default="#EAECEE")
    BG_COLOR: str = dc.field(init=True, default="#18181B")
    BG_GRAY: str = dc.field(init=True, default="#4B4B4F")

    FONT: str = dc.field(init=True, default="Helvetica 10")

    window: tk.Tk = dc.field(init=False, default=tk.Tk())
    receive_queue: list = dc.field(init=False, default=queue.Queue())
    send_queue: list = dc.field(init=False, default=queue.Queue())

    text_widget: tk.Text = dc.field(init=False)
    msg_entry: tk.Entry = dc.field(init=False)

    known_users: set = dc.field(init=False, default_factory=set)

    def __post_init__ (self) -> None:
        self.window.title(f"Zap Chat")
        self.window.resizable(width=True, height=True)
        self.window.configure(bg=self.BG_COLOR)

        # Text Widjet
        self.text_widget = tk.Text(
            self.window, bg=self.BG_COLOR, fg=self.TEXT_COLOR,
            font=self.FONT, padx=5, pady=8, spacing1=0, spacing2=1, spacing3=3
        )
        self.text_widget.place(relheight=0.970, relwidth=1)

        # Adding Default User Tag
        self.text_widget.tag_config(
            "DEFAULT_USER", font=self.FONT + " bold", foreground=self.TEXT_COLOR
        )

        # Bottom Label
        bottom_label = tk.Label(self.window, bg=self.BG_COLOR, height=20)
        bottom_label.place(relwidth=1, relheight=1, rely=0.968, )

        # Message Entry Box
        self.msg_entry = tk.Entry(
            bottom_label, bg=self.BG_GRAY, fg=self.TEXT_COLOR, font=self.FONT,
            borderwidth=5, relief=tk.FLAT
        )
        self.msg_entry.place(relwidth=1, relheight=0.03)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self.save_message)

    async def run (self) -> None:
        threading.Thread(target=self.api_handler, daemon=True).start()

        self.event_handler()
        self.window.mainloop()

    def event_handler (self) -> None:
        try:
            msg, user, kwargs = self.receive_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            self._insert_message(msg, user, **kwargs)

        self.window.after(150, self.event_handler)

    def api_handler (self) -> None:
        asyncio.run(self._api_handler())

    async def _api_handler (self) -> None:
        while True:
            consumer_task = asyncio.create_task(self.receive_message())
            producer_task = asyncio.create_task(self.parse_command())

            done, pending = await asyncio.wait(
                [ consumer_task, producer_task ],
                return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()

    async def receive_message (self) -> None:
        await asyncio.sleep(5)

    def _format_ip (self, new_ip: str, old_url: str) -> str:
        old_splits = old_url.split(":")
        return old_splits[0] + ":" + new_ip + ":" + old_splits[2]

    async def print_api (self) -> None:
        print(f"user id: {api.user_id}")
        print(f"base url: {api.base_url}")
        print(f"device url: {api.device_url}")

    async def update_url (self, new_ip: str) -> None:
        api.base_url = self._format_ip(new_ip, api.base_url)
        api.device_url = self._format_ip(new_ip, api.device_url)

    async def info_model (self, mdl_name: str, id: str) -> None:
        models = {
            "chat": Chat,
            "user": User,
            "message": Message,
        }

        model = models[mdl_name]
        if id == "all":
            print(json.dumps(model.query.all(), cls=AlchemyEncoder))

        else:
            obj = model.query.filter_by(id=id).one()
            print(json.dumps(obj, cls=AlchemyEncoder))

    async def signup_user (self, name: str, password: str, telephone: str) -> None:
        api.signup(name, telephone, password)

    async def create_chat (self, chat_name: str, user_tel: str) -> None:
        chat_id = api.create_chat(chat_name, [ user_tel ])
        print(f"the new chat-id is {chat_id}")

    async def send_message (self, chat_id: str, message: str) -> None:
        print(api.send_message(chat_id, message))
        self._insert_message(message + '\n', "eu")

    async def ping (self) -> None:
        print(api.ping())

    async def help_ui (self) -> None:
        print("the commands allowed are the following")
        print("print: to get information about api attributes")
        print(
            "info::<MODEL>::<ID>: print information about a object from <MODEL> " + \
            "or all of them, decoded to a json::style object"
        )
        print(
            "signup::<NAME>::<TELEPHONE>::<PASSWORD>: " + \
            "creates the user and make it's login with the api."
        )
        print(
            "create::chat::<CHAT_NAME>::<RCV_TEL>: creates a chat room " + \
            " with the owner of the selected telephone"
        )
        print(
            "send::message::<CHAT_ID>::<MESSAGE>: sends the message to " + \
            "the chat's participants"
        )
        print("ping: tests the connection with the server")
        print("exit: closes the application")

    async def not_found (self) -> None:
        print("help for more informations")

    def save_message (self, event: any) -> None:
        message = self.msg_entry.get()
        self.msg_entry.delete(0, tk.END)

        self.send_queue.put(message)

    async def parse_command (self) -> None:
        try:
            command = self.send_queue.get(block=False)

        except queue.Empty:
            await asyncio.sleep(5)

        else:
            action_info = command.split("::")
            action = action_info[0]

            if action == "print":
                return await self.print_api()

            elif action == "update-url":
                new_ip = action_info[1]
                return await self.update_url(new_ip)

            elif action == "info":
                mdl_name = action_info[1]
                obj_id = action_info[2]
                return await self.info_model(mdl_name, obj_id)

            elif action == "signup":
                user_name = action_info[1]
                telephone = action_info[2]
                password = action_info[3]
                return await self.signup_user(user_name, password, telephone)

            elif action == "create-chat":
                chat_name = action_info[1]
                rcv_tel = action_info[2]
                return await self.create_chat(chat_name, rcv_tel)

            elif action == "send-message":
                chat_id = action_info[1]
                message = action_info[ 2 : ]
                return await self.send_message(chat_id, message)

            elif action == "ping":
                return await self.ping()

            elif action == "help":
                return await self.help_ui()

            elif action == "exit":
                exit()

            else:
                return await self.not_found()

    def _insert_message(
        self, raw_msg: str, sender: str, color: str = None, emotes: str = None, badges: str = None
    ) -> None:
        if raw_msg == "":
            return
        if color is not None:
            self.text_widget.tag_config(sender, font=self.FONT + " bold", foreground=color)

            self.known_users.add(sender)
            tag = sender
        else:
            tag = "DEFAULT_USER"

        self.text_widget.configure(state=tk.NORMAL)

        self.text_widget.insert(tk.END, f"{sender}", tag)
        self.text_widget.insert(tk.END, f": {raw_msg}\n")

        self.text_widget.configure(state=tk.DISABLED)

        self.text_widget.see(tk.END)
