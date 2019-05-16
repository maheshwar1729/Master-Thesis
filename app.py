from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib.parse import unquote


app = Flask(__name__)
CORS(app)


@app.route("/")
def log():
    with open("genes.csv", "a") as f:
        s = unquote(request.args.get("event"))
        if s.find('fps') != -1:
            return jsonify({})
        f.write(unquote(request.args.get("event")))
        f.write("\n")
    f.close()
    return jsonify({})
