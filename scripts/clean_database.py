from app.services import chat as chsr
from app.services import user as ussr

chsr.init_chat_db()
ussr.init_user_db()