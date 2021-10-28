from app import db

from . import user_chat

# Define a User model
class User (db.Model):

    __tablename__   : str = "user"
    user_id         : db.Integer = db.Column(db.Integer, primary_key=True)

    # User Name
    name            : db.String = db.Column(db.String(128), nullable=False)

    # Identification Data: email & password
    email           : db.String = db.Column(db.String(128), nullable=False, unique=True)
    password        : db.String = db.Column(db.String(192), nullable=False)

    date_created    : db.DateTime = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified   : db.DateTime = db.Column(
        db.DateTime,  default=db.func.current_timestamp(), onupdate=db.func.current_timestamp()
    )

    # Extra Information
    telephone       : db.String = db.Column(db.String(15), nullable=True)
    description     : db.Text = db.Column(db.Text(500), nullable=True)

    # Foreign Keys
    messages        : any = db.relationship("Message", backref='sender')
    chats           : any = db.relationship(
        "Chat", secondary=user_chat, backref=db.backref("users", lazy="dynamic")
    )

    def __repr__ (self) -> str:
        return f"<User {self.name}>"
