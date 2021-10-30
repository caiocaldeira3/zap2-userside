from app import db

# Define a Chat model
class Chat (db.Model):

    __tablename__   : str = "chat"
    chat_id         : db.Integer = db.Column(db.Integer, primary_key=True)

    # Chat Name
    name            : db.String = db.Column(db.String(128), nullable=False)

    date_created    : db.DateTime = db.Column(db.DateTime, default=db.func.now())
    date_modified   : db.DateTime = db.Column(
        db.DateTime,  default=db.func.now(), onupdate=db.func.now()
    )

    # Extra Information
    description     : db.Text = db.Column(db.Text(500), nullable=True)

    def __repr__ (self) -> str:
        return f"<Chat {self.name}>"
