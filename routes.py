from flask import Blueprint, request, jsonify, render_template
from handlers import chats, handle_message
from config import VERIFY_TOKEN
import json

webhook_routes = Blueprint('webhook', __name__)
chat_routes = Blueprint('chat', __name__)

@webhook_routes.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verification token mismatch", 403

    data = request.get_json()
    print(f"Received message: {data}")

    if 'entry' in data:
        for entry in data['entry']:
            for change in entry['changes']:
                if 'messages' in change['value']:
                    for message in change['value']['messages']:
                        handle_message(message)
    return "OK", 200

@chat_routes.route("/")
def index():
    return render_template("index.html")


@chat_routes.route("/api/chats", methods=["GET"])
def get_chats():
    chat_list = [
        {
            "id": chat_id,
            "name": chat_data["name"],
            "avatar_url": "/static/avatars/default.webp",
            "last_message_time": chat_data["last_message_time"]
        }
        for chat_id, chat_data in chats.items()
    ]
    return jsonify(chat_list)

@chat_routes.route("/api/chats/<chat_id>/messages", methods=["GET"])
def get_messages(chat_id):
    if chat_id in chats:
        return jsonify(chats[chat_id]["messages"])
    return jsonify([])

@chat_routes.route("/api/chats/<chat_id>/update_name", methods=["POST"])
def update_chat_name(chat_id):
    data = request.get_json()
    new_name = data.get("name")
    if chat_id in chats:
        chats[chat_id]["name"] = new_name
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Chat not found"}), 404



@chat_routes.route("/api/save_welcome_message", methods=["POST"])
def save_welcome_message():
    data = request.get_json()
    try:
        with open("welcome_message.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@chat_routes.route("/api/save_services_list", methods=["POST"])
def save_services_list():
    data = request.get_json()
    try:
        with open("services_list.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    


@chat_routes.route("/api/save_buttons_list", methods=["POST"])
def save_buttons_list():
    data = request.get_json()
    try:
        with open("buttons_list.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@chat_routes.route("/api/save_faq_list", methods=["POST"])
def save_faq_list():
    data = request.get_json()
    try:
        with open("faq_list.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500