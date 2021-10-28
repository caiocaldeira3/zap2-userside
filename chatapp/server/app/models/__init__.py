from app import db

user_chat = db.Table(
    "user_chat",
    db.Column("user_id", db.Integer, db.ForeignKey("user.user_id")),
    db.Column("chat_id", db.Integer, db.ForeignKey("chat.chat_id"))
)