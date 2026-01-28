from flask import Flask, render_template, request, jsonify
from core import get_response

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    # Validasi data
    if not data or "message" not in data:
        return jsonify({"reply": "Pesan tidak boleh kosong"}), 400

    message = data["message"]
    reply = get_response(message, user_id="web_user")  # user_id tetap untuk web

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)