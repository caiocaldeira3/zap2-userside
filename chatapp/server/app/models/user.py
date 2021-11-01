from app import db

from . import user_chat

# Define a User model
class User (db.Model):

    __tablename__   : str = "user"
    id         : db.Integer = db.Column(db.Integer, primary_key=True)

    # User Name
    name            : db.String = db.Column(db.String(128), nullable=False)

    # Identification Data: email & password
    email           : db.String = db.Column(db.String(128), nullable=False, unique=True)
    telephone       : db.String = db.Column(db.String(15), nullable=False, unique=True)
    id_key          : db.String = db.Column(db.String(128), nullable=False)
    sgn_key         : db.String = db.Column(db.String(128), nullable=False)

    date_created    : db.DateTime = db.Column(db.DateTime, default=db.func.now())
    date_modified   : db.DateTime = db.Column(
        db.DateTime,  default=db.func.now(), onupdate=db.func.now()
    )

    # Extra Information
    description     : db.Text = db.Column(db.Text(500), nullable=True)

    # Foreign Keys
    otkeys         : any = db.relationship("OTKey", backref="owner")
    devices         : any = db.relationship("Device", backref="user")
    # chats           : any = db.relationship(
    #     "Chat", secondary=user_chat, backref=db.backref("users", lazy="dynamic")
    # )

    def __repr__ (self) -> str:
        return f"<User {self.name}>"