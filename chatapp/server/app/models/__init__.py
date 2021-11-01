from app import db

user_chat = db.Table(
    "user_chat",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("chat_id", db.Integer, db.ForeignKey("chat.id"))
)