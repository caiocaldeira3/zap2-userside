from app import db

from . import user_chat

# Define a Chat model
class Chat (db.Model):

    __tablename__   : str = "chat"
    id         : db.Integer = db.Column(db.Integer, primary_key=True)

    # Chat Name
    name            : db.String = db.Column(db.String(128), nullable=False)

    date_created    : db.DateTime = db.Column(db.DateTime, default=db.func.now())
    date_modified   : db.DateTime = db.Column(
        db.DateTime,  default=db.func.now(), onupdate=db.func.now()
    )

    # Extra Information
    description     : db.Text = db.Column(db.Text(500), nullable=True)

    # Foreign Keys
    # messages        : any = db.relationship("Message", backref="sender")
    chats           : any = db.relationship(
        "Chat", secondary=user_chat, backref=db.backref("users", lazy="dynamic")
    )

    def __repr__ (self) -> str:
        return f"<Chat {self.user.name}>"
