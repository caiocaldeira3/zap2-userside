from app import db

# Define a OTKey model
class OTKey (db.Model):

    __tablename__   : str = "otkey"
    id          : db.Integer = db.Column(db.Integer, primary_key=True)

    user_id     : db.Integer = db.Column(db.Integer, db.ForeignKey("user.id"))
    key_id      : db.Integer = db.Column(db.Integer, nullable=False)
    otkey       : db.String = db.Column(db.String(64), nullable=False)

    def __repr__ (self) -> str:
        return f"<{self.owner}  {self.otkey}>"
