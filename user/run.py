import sys
import asyncio

from app import app
from app.util.chat_ui import ZapChat

if __name__ == "__main__":
    if len(sys.argv) == 3:
        # zap = ZapChat("eu: ")
        # asyncio.run(zap.run())

        app.run(host="0.0.0.0", port=sys.argv[2], debug=True)

    else:
        # zap = ZapChat("eu: ")
        # asyncio.run(zap.run())

        app.run(host="0.0.0.0", port=3030, debug=True)