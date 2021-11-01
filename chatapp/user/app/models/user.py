from app import db

# Define a User model
class User (db.Model):

    __tablename__   : str = "user"
    id         : db.Integer = db.Column(db.Integer, primary_key=True)

    # User Name
    name            : db.String = db.Column(db.String(128), nullable=False)

    # Identification Data: email & telephone & password & id on server
    email           : db.String = db.Column(db.String(128), nullable=False, unique=True)
    telephone       : db.String = db.Column(db.String(15), nullable=False, unique=True)
    server_id       : db.Integer = db.Column(db.Integer, nullable=False, unique=True)
    password        : db.String = db.Column(db.String(128), nullable=False)

    # Attributes
    description     : db.String = db.Column(db.String(255), nullable=True)

    # Foreign Keys
    # chats           : any = db.relationship("Chat", backref=db.backref("users"))
    # messages        : any = db.relationship("Message", backref="sender")

    def __repr__ (self) -> str:
        return f"<User {self.name}>"
