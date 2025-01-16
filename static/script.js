document.addEventListener("DOMContentLoaded", function () {
    const chatList = document.getElementById("chat-list");
    const chatMessages = document.getElementById("chat-messages");
    const messageInput = document.getElementById("message-input");
    const sendButton = document.getElementById("send-button");
    const chatTitle = document.getElementById("chat-title");
    const welcomeScreen = document.getElementById("welcome-screen");
    const chatHeader = document.querySelector(".chat-header");
    const chatInput = document.querySelector(".chat-input");
    const popupOverlay = document.getElementById('popup-overlay');
    const editNameInput = document.getElementById('edit-name-input');
    const saveNameButton = document.getElementById('save-name-button');
    const cancelEditButton = document.getElementById('cancel-edit-button');
    const backToChatsButton = document.getElementById('back-to-chats');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');


    let currentChatId = null;

    // الاتصال بـ WebSocket
    const socket = io();




    // استقبال تحديثات الرسائل
    // استقبال رسالة جديدة
// استقبال رسالة جديدة
socket.on('new_message', function (data) {
    console.log("New message received:", data);  // Debugging
    console.log("Current chat ID:", currentChatId);  // Debugging

    // إذا كانت الرسالة موجهة للمحادثة الحالية، قم بتحديث الواجهة
    if (data.chat_id === currentChatId) {
        console.log("Updating chat messages...");  // Debugging
        const messageDiv = document.createElement("div");
        messageDiv.className = data.message.sender === "bot" ? "message bot" : "message user";
        messageDiv.innerHTML = `
            <div class="message-content">${data.message.text}</div>
            <div class="timestamp">${data.message.timestamp}</div>
        `;
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    } else {
        // إشعار عند وصول رسالة جديدة
        if (Notification.permission === "granted") {
            new Notification("رسالة جديدة", {
                body: data.message.text,
                icon: avatarUrl  // استخدام المتغير الذي تم تمريره
            });
        }
    }

    // تحديث قائمة المحادثات تلقائيًا
    fetchChats();
});




// تفعيل حقل الإدخال عند اختيار محادثة
function enableChatInput() {
    messageInput.disabled = false;
    sendButton.disabled = false;
}

// طلب إذن الإشعارات
if (Notification.permission !== "granted") {
    Notification.requestPermission();
}




    function showChat() {
        sidebar.classList.add('hidden');
        mainContent.classList.add('active');
    }

    // إظهار قائمة المحادثات وإخفاء الدردشة على الهواتف
    function showChatList() {
        sidebar.classList.remove('hidden');
        mainContent.classList.remove('active');
    }

    // حدث النقر على زر العودة
    backToChatsButton.addEventListener('click', showChatList);




    // إرسال رسالة من الواجهة
    function sendMessage() {
        const messageText = messageInput.value.trim();
        if (messageText && currentChatId) {
            // إرسال الرسالة إلى الخادم عبر WebSocket
            socket.emit('send_message', {
                chat_id: currentChatId,
                text: messageText
            });
            // مسح حقل الإدخال
            messageInput.value = "";
            scrollToBottom();
        }
    }

    // إرسال الرسالة عند الضغط على زر الإرسال
    sendButton.addEventListener("click", sendMessage);

    // إرسال الرسالة عند الضغط على Enter
    messageInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    // دالة لتمرير منطقة الرسائل إلى الأسفل
function scrollToBottom() {
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// البحث في قائمة المحادثات
document.getElementById("search-chats-input").addEventListener("input", function (e) {
    const searchTerm = e.target.value.toLowerCase();
    const chatItems = document.querySelectorAll("#chat-list li");

    chatItems.forEach(chat => {
        const chatName = chat.querySelector(".chat-info h3").textContent.toLowerCase();
        if (chatName.includes(searchTerm)) {
            chat.style.display = "flex";  // إظهار المحادثة إذا تطابقت مع البحث
        } else {
            chat.style.display = "none";  // إخفاء المحادثة إذا لم تتطابق
        }
    });
});

// البحث في رسائل الدردشة
document.getElementById("search-messages-input").addEventListener("input", function (e) {
    const searchTerm = e.target.value.toLowerCase();
    const messages = document.querySelectorAll("#chat-messages .message");

    messages.forEach(message => {
        const messageText = message.querySelector(".message-content").textContent.toLowerCase();
        if (messageText.includes(searchTerm)) {
            message.style.display = "block";  // إظهار الرسالة إذا تطابقت مع البحث
        } else {
            message.style.display = "none";  // إخفاء الرسالة إذا لم تتطابق
        }
    });
});

    // تفعيل حقل الإدخال عند اختيار محادثة
    function enableChatInput() {
        messageInput.disabled = false;
        sendButton.disabled = false;
    }

    // طلب إذن الإشعارات
    if (Notification.permission !== "granted") {
        Notification.requestPermission();
    }


    function formatDateTime(dateTimeString) {
        const date = new Date(dateTimeString);
        const options = {
            weekday: 'short',  // يوم الأسبوع (مثل "أحد")
            hour: '2-digit',   // الساعة (مثل "01")
            minute: '2-digit', // الدقيقة (مثل "05")
            hour12: true       // استخدام نظام 12 ساعة (ص/م)
        };
        return date.toLocaleString('ar-SA', options);  // استخدام التنسيق العربي
    }

    // دالة لجلب المحادثات من الخادم
    async function fetchChats() {
        try {
            const response = await fetch("/api/chats");
            const chats = await response.json();
            chatList.innerHTML = "";
            chats.forEach(chat => {
                const li = document.createElement("li");
                li.innerHTML = `
                    <img src="${avatarUrl}" alt="User Avatar" class="chat-avatar">
                    <div class="chat-info">
                        <h3>${chat.name}</h3>
                        <p>آخر ظهور: ${formatDateTime(chat.last_message_time)}</p>
                    </div>
                    <button class="mark-important" data-chat-id="${chat.id}">تعيين اسم</button>
                    <input type="text" class="edit-name" data-chat-id="${chat.id}" placeholder="تعديل الاسم" style="display: none;">
                `;
                li.addEventListener("click", () => {
                    console.log("Chat clicked, setting currentChatId to:", chat.id);  // Debugging
                    currentChatId = chat.id;
                    loadChat(chat.id);
                    welcomeScreen.style.display = "none";  // إخفاء قسم الترحيب
                    chatHeader.classList.add('active');  // إظهار شريط الدردشة
                    chatInput.classList.add('active');  // إظهار حقل الإدخال
                    enableChatInput();  // تفعيل حقل الإدخال
                    showChat();  // إظهار الدردشة على الهواتف
                });
                chatList.appendChild(li);
            });
    
            // إضافة حدث النقر على زر "تعيين كمهم"
            document.querySelectorAll('.mark-important').forEach(button => {
                button.addEventListener('click', function(event) {
                    event.stopPropagation();  // منع انتشار الحدث إلى العنصر الأب
                    currentChatId = this.getAttribute('data-chat-id');
                    popupOverlay.style.display = 'flex';  // إظهار النافذة المنبثقة
                    editNameInput.focus();
                });
            });
            
            // حفظ الاسم الجديد
            saveNameButton.addEventListener('click', function() {
                const newName = editNameInput.value.trim();
                if (newName) {
                    updateChatName(currentChatId, newName);
                    popupOverlay.style.display = 'none';  // إخفاء النافذة المنبثقة
                }
            });
            
            // إلغاء التعديل
            cancelEditButton.addEventListener('click', function() {
                popupOverlay.style.display = 'none';  // إخفاء النافذة المنبثقة
            });
    
            // إضافة حدث لإدخال الاسم الجديد
            document.querySelectorAll('.edit-name').forEach(input => {
                input.addEventListener('keydown', function(event) {
                    if (event.key === 'Enter') {
                        const chatId = this.getAttribute('data-chat-id');
                        const newName = this.value.trim();
                        if (newName) {
                            updateChatName(chatId, newName);
                            this.style.display = 'none';
                        }
                    }
                });
            });
        } catch (error) {
            console.error("Failed to fetch chats:", error);
        }
    }



    
    async function updateChatName(chatId, newName) {
        try {
            const response = await fetch(`/api/chats/${chatId}/update_name`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: newName }),
            });
            if (response.ok) {
                fetchChats();  // تحديث قائمة المحادثات بعد التعديل
            } else {
                console.error("Failed to update chat name:", response.statusText);
            }
        } catch (error) {
            console.error("Error updating chat name:", error);
        }
    }

    // دالة لجلب الرسائل الخاصة بمحادثة معينة
    async function loadChat(chatId) {
        try {
            const response = await fetch(`/api/chats/${chatId}/messages`);
            const messages = await response.json();
            chatMessages.innerHTML = "";
            messages.forEach(message => {
                const messageDiv = document.createElement("div");
                messageDiv.className = message.sender === "bot" ? "message bot" : "message user";
                messageDiv.innerHTML = `
                    <div class="message-content">${message.text}</div>
                    <div class="timestamp">${message.timestamp}</div>
                `;
                chatMessages.appendChild(messageDiv);
            });
            chatTitle.textContent = `${chatId}  `;
            document.getElementById("search-messages-input").disabled = false;  // تفعيل حقل البحث
            scrollToBottom();
        } catch (error) {
            console.error("Failed to load chat:", error);
        }
        
    }   

    // جلب المحادثات عند تحميل الصفحة
    fetchChats();
});