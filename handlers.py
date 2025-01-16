from datetime import datetime
import json
import requests
from config import ACCESS_TOKEN, PHONE_NUMBER_ID



# تخزين المحادثات
chats = {}

# تعريف الدالة handle_message في النطاق العام
def handle_message(message):
    sender_id = message['from']
    if sender_id not in chats:
        chats[sender_id] = {
            "name": f"{sender_id}",
            "last_message_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "messages": []
        }

    if 'text' in message:
        text = message['text']['body'].lower()
        chats[sender_id]["messages"].append({
            "sender": "user",
            "text": text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        chats[sender_id]["last_message_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        socketio.emit('new_message', {'chat_id': sender_id, 'message': chats[sender_id]["messages"][-1]})
        send_browser_notification(sender_id, chats[sender_id]["messages"][-1]['text'])
        if 'text' in message:
            text = message['text']['body'].strip()
            if text:
                send_welcome_message(sender_id)

    elif 'interactive' in message:
        interactive_data = message['interactive']
        if interactive_data['type'] == 'list_reply':
            list_reply_id = interactive_data['list_reply']['id']
            chats[sender_id]["messages"].append({
                "sender": "user",
                "text": f"اختار: {list_reply_id}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            chats[sender_id]["last_message_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            socketio.emit('new_message', {'chat_id': sender_id, 'message': chats[sender_id]["messages"][-1]})
            if list_reply_id == 'services':
                send_services_list(sender_id)
            elif list_reply_id in ['digital_marketing', 'graphic_design', 'seo', 'ecommerce_dev', 'mobile_apps']:
                send_waiting_message(sender_id)
            else:
                send_waiting_message(sender_id)

def send_browser_notification(chat_id, message_text):
    socketio.emit('browser_notification', {'chat_id': chat_id, 'message': message_text})                

# تعريف الدوال الأخرى في النطاق العام
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
            "header": {"type": "text", "text": "حياك الله مرحبا بك :"},
            "body": {"text": "مؤسسة جو سيرف للتسويق الالكتروني 👉🤍🌹"},
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
    
    # إرسال تحديث إلى الواجهة عبر WebSocket
    socketio.emit('new_message', {'chat_id': recipient_id, 'message': chats[recipient_id]["messages"][-1]})

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

def send_waiting_message(recipient_id):
    send_text_message(recipient_id, "🤍🌹 برجاء الانتظار تم تحويلك للقسم المختص للتواصل معك")

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
    chats[recipient_id]["messages"].append({
        "sender": "bot",
        "text": text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    socketio.emit('new_message', {'chat_id': recipient_id, 'message': chats[recipient_id]["messages"][-1]})

# تعريف register_handlers
def register_handlers(socketio_instance):
    global socketio
    socketio = socketio_instance

    @socketio.on('send_message')
    def handle_send_message(data):
        chat_id = data['chat_id']
        text = data['text']
        send_text_message(chat_id, text)