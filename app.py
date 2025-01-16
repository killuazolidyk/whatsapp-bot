from flask import Flask # type: ignore
from flask_socketio import SocketIO # type: ignore
from routes import webhook_routes, chat_routes
from handlers import register_handlers

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# تسجيل الروابط
app.register_blueprint(webhook_routes)
app.register_blueprint(chat_routes)

# تسجيل معالجات الرسائل
register_handlers(socketio)

if __name__ == "__main__":
    socketio.run(app, debug=True)






""" from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import requests
import json
from datetime import datetime
import os
from werkzeug.utils import secure_filename


app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)  # تفعيل Debug Mode

ACCESS_TOKEN = "access token"
VERIFY_TOKEN = "my_token"
PHONE_NUMBER_ID = "id"

# تخزين المحادثات
chats = {}

def generate_avatar_url(chat_id):
    
    إنشاء رابط الصورة الرمزية باستخدام الصور المحلية.
    
    avatar_filename = f"{chat_id}.webp"
    avatar_url = f"/static/avatars/{avatar_filename}"  # المسار النسبي للصورة
    return avatar_url

@app.route("/")
def index():
    return render_template("index.html")



@app.route("/api/chats", methods=["GET"])
def get_chats():
    chat_list = [
        {
            "id": chat_id,
            "name": chat_data["name"],
            "avatar_url": "/static/avatars/default.webp",  # صورة افتراضية
            "last_message_time": chat_data["last_message_time"]
        }
        for chat_id, chat_data in chats.items()
    ]
    return jsonify(chat_list)




@app.route("/api/chats/<chat_id>/messages", methods=["GET"])
def get_messages(chat_id):
    if chat_id in chats:
        return jsonify(chats[chat_id]["messages"])
    return jsonify([])




@app.route("/webhook", methods=["GET", "POST"])
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




@app.route("/api/chats/<chat_id>/update_name", methods=["POST"])
def update_chat_name(chat_id):
    data = request.get_json()
    new_name = data.get("name")
    if chat_id in chats:
        chats[chat_id]["name"] = new_name
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Chat not found"}), 404



# التعامل مع الرسائل
def handle_message(message):
    sender_id = message['from']
    if sender_id not in chats:
        chats[sender_id] = {
            "name": f"{sender_id}",  # اسم افتراضي
            "last_message_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "messages": []
        }

    if 'text' in message:
        text = message['text']['body'].lower()
        # حفظ رسالة العميل
        chats[sender_id]["messages"].append({
            "sender": "user",
            "text": text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        # تحديث وقت آخر رسالة
        chats[sender_id]["last_message_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # إرسال تحديث إلى الواجهة عبر WebSocket
        socketio.emit('new_message', {'chat_id': sender_id, 'message': chats[sender_id]["messages"][-1]})
        if 'text' in message:
            text = message['text']['body'].strip()  # إزالة الفراغات الزائدة
            if text:  # إذا كان النص غير فارغ
               send_welcome_message(sender_id)
    
    elif 'interactive' in message:
        interactive_data = message['interactive']
        if interactive_data['type'] == 'list_reply':
            list_reply_id = interactive_data['list_reply']['id']
            # حفظ اختيار العميل
            chats[sender_id]["messages"].append({
                "sender": "user",
                "text": f"اختار: {list_reply_id}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            # تحديث وقت آخر رسالة
            chats[sender_id]["last_message_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # إرسال تحديث إلى الواجهة عبر WebSocket
            socketio.emit('new_message', {'chat_id': sender_id, 'message': chats[sender_id]["messages"][-1]})
            if list_reply_id == 'services':
                send_services_list(sender_id)
            elif list_reply_id in [
                'digital_marketing',
                'graphic_design',
                'seo',
                'ecommerce_dev',
                'mobile_apps']:
                send_waiting_message(sender_id)
            else:
                send_waiting_message(sender_id)

# استقبال الرسائل من الواجهة
@socketio.on('send_message')
def handle_send_message(data):
    chat_id = data['chat_id']
    text = data['text']
    send_text_message(chat_id, text)

# إرسال رسالة ترحيب
def send_welcome_message(recipient_id):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_id,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": " حياك الله مرحبا بك :"},
            "body": {"text": " منصه ميثاق نجاح للتسويق الالكتروني نجاحك ميثاق علينا 👉🤍🌹 :"},
            "action": {
                "button": "القائمة",
                "sections": [
                    {
                        "title": "الخدمات",
                        "rows": [
                            {"id": "services", "title": "الخدمات", "description": "استعرض خدماتنا المختلفة."},
                            {"id": "free_consultation", "title": "استشارات مجانية", "description": "استشارة مجانية من فريقنا."},
                            {"id": "customer_service", "title": "خدمة العملاء", "description": "تحدث مع ممثل خدمة العملاء."}
                        ]
                    }
                ]
            }
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(response.status_code, response.text)
    # حفظ رد البوت
    chats[recipient_id]["messages"].append({
        "sender": "bot",
        "text": "مرحبًا! كيف يمكنني مساعدتك؟",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    # إرسال تحديث إلى الواجهة عبر WebSocket
    socketio.emit('new_message', {'chat_id': recipient_id, 'message': chats[recipient_id]["messages"][-1]})

# إرسال قائمة الخدمات
def send_services_list(recipient_id):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_id,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "اختر الخدمة التي تحتاجها :"
            },
            "body": {
                "text": "الخدمات المتاحة :"
            },
            "action": {
                "button": "اختر الخدمة",
                "sections": [
                    {
                        "title": "قائمة الخدمات",
                        "rows": [
                            {
                                "id": "digital_marketing",
                                "title": "تسويق الكتروني",
                                "description": "خدمات التسويق الرقمي"
                            },
                            {
                                "id": "graphic_design",
                                "title": "تصميم جرافيك",
                                "description": "تصميمات مرئية احترافية"
                            },
                            {
                                "id": "seo",
                                "title": "تحسين محركات البحث SEO",
                                "description": "رفع ترتيب محركات البحث"
                            },
                            {
                                "id": "store_management",
                                "title": "ادارة متاجر الكترونية",
                                "description": "إدارة وتطوير المتاجر"
                            },
                            {
                                "id": "app_dev",
                                "title": "تطوير تطبيقات الجوال",
                                "description": "برمجة تطبيقات الجوال"
                            }
                        ]
                    }
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(response.status_code, response.text)
    # حفظ رد البوت
    chats[recipient_id]["messages"].append({
        "sender": "bot",
        "text": "اختر الخدمة التي تحتاجها من القائمة.",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    # إرسال تحديث إلى الواجهة عبر WebSocket
    socketio.emit('new_message', {'chat_id': recipient_id, 'message': chats[recipient_id]["messages"][-1]})

# إرسال رسالة انتظار
def send_waiting_message(recipient_id):
    send_text_message(recipient_id, "🤍🌹 برجاء الانتظار تم تحويلك للقسم المختص للتواصل معك")

# إرسال نص عادي
def send_text_message(recipient_id, text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": text}
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(response.status_code, response.text)
    # حفظ رد البوت
    chats[recipient_id]["messages"].append({
        "sender": "bot",
        "text": text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    # إرسال تحديث إلى الواجهة عبر WebSocket
    socketio.emit('new_message', {'chat_id': recipient_id, 'message': chats[recipient_id]["messages"][-1]})

if __name__ == "__main__":
    socketio.run(app, debug=True)





 """