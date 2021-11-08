import sys
from app import app

if __name__ == "__main__":
    if len(sys.argv) == 3:
        app.run(host="0.0.0.0", port=sys.argv[2], debug=True)
    else:
        app.run(host="0.0.0.0", port=3030, debug=True)