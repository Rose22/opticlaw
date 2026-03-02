import asyncio
from flask import Flask, render_template_string, request, jsonify, cli
import core
from threading import Thread
import logging

app = Flask(__name__)

# disable all logs
cli.show_server_banner = lambda *x: print(end="")
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
log.disabled = True

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat with AI</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        html, body {
            height: 100%;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
        }
        .app-container {
            display: flex;
            flex-direction: column;
            height: 100%;
            max-width: 900px;
            margin: 0 auto;
            background: #111111;
            box-shadow: 0 0 40px rgba(0,0,0,0.8);
        }
        header {
            padding: 16px 20px;
            background: linear-gradient(180deg, #1a1a1a 0%, #0f0f0f 100%);
            border-bottom: 1px solid #2a2a2a;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        header h1 {
            font-size: 1.3rem;
            font-weight: 600;
            color: #e8e8e8;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            background: #4ade80;
            border-radius: 50%;
            box-shadow: 0 0 10px rgba(74,222,128,0.6);
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: #0d0d0d;
        }
        .message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 16px;
            line-height: 1.5;
            word-wrap: break-word;
            animation: slideIn 0.2s ease-out;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user {
            align-self: flex-end;
            background: linear-gradient(135deg, #3a3a3a 0%, #2d2d2d 100%);
            color: #f0f0f0;
            border: 1px solid #444444;
            border-bottom-right-radius: 4px;
        }
        .message.ai {
            align-self: flex-start;
            background: #1a1a1a;
            border: 1px solid #333333;
            color: #d0d0d0;
            border-bottom-left-radius: 4px;
        }
        .message.announce {
            align-self: center;
            background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
            border: 1px solid #404040;
            color: #a0a0a0;
            font-style: italic;
            text-align: center;
            font-size: 0.9rem;
            max-width: 90%;
        }
        .input-area {
            padding: 16px;
            background: #0a0a0a;
            border-top: 1px solid #222222;
            display: flex;
            gap: 12px;
            align-items: center;
        }
        #message {
            flex: 1;
            padding: 14px 18px;
            border: 1px solid #2a2a2a;
            border-radius: 24px;
            background: #161616;
            color: #e0e0e0;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        #message:focus {
            border-color: #555555;
            box-shadow: 0 0 0 3px rgba(80,80,80,0.3);
        }
        #message::placeholder {
            color: #555555;
        }
        #send {
            padding: 14px 24px;
            background: linear-gradient(135deg, #3a3a3a 0%, #2a2a2a 100%);
            border: 1px solid #444444;
            border-radius: 24px;
            color: #e0e0e0;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.1s, background 0.2s;
        }
        #send:hover {
            background: linear-gradient(135deg, #444444 0%, #333333 100%);
        }
        #send:active {
            transform: scale(0.96);
        }
        .typing-indicator {
            display: none;
            align-self: flex-start;
            padding: 12px 16px;
            background: #1a1a1a;
            border: 1px solid #333333;
            border-radius: 16px;
            border-bottom-left-radius: 4px;
        }
        .typing-indicator.show {
            display: flex;
            gap: 4px;
            align-items: center;
        }
        .typing-indicator span {
            width: 8px;
            height: 8px;
            background: #555555;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out;
        }
        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0.8); }
            40% { transform: scale(1.2); }
        }
        .chat-container::-webkit-scrollbar {
            width: 6px;
        }
        .chat-container::-webkit-scrollbar-track {
            background: #0a0a0a;
        }
        .chat-container::-webkit-scrollbar-thumb {
            background: #2a2a2a;
            border-radius: 3px;
        }
        .chat-container::-webkit-scrollbar-thumb:hover {
            background: #3a3a3a;
        }
        @media (max-width: 600px) {
            header h1 { font-size: 1.1rem; }
            .message { max-width: 90%; padding: 10px 14px; }
            #send { padding: 14px 18px; }
        }
    </style>
</head>
<body>
    <div class="app-container">
        <header>
            <div class="status-dot"></div>
            <h1>Chat with AI</h1>
        </header>
        <div class="chat-container" id="chat">
            <div class="typing-indicator" id="typing">
                <span></span><span></span><span></span>
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="message" placeholder="Type a message..." onkeypress="if(event.key==='Enter')send()">
            <button id="send" onclick="send()">Send</button>
        </div>
    </div>
    <script>
        let lastAnnouncementId = 0;
        const chat = document.getElementById('chat');
        const typing = document.getElementById('typing');

        function addMessage(role, content) {
            const div = document.createElement('div');
            div.className = 'message ' + role;
            div.textContent = content;
            chat.insertBefore(div, typing);
            chat.scrollTop = chat.scrollHeight;
        }

        async function pollAnnouncements() {
            try {
                const response = await fetch('/poll?id=' + lastAnnouncementId);
                const data = await response.json();
                if (data.messages) {
                    for (const msg of data.messages) {
                        addMessage('announce', msg.content);
                        lastAnnouncementId = msg.id;
                    }
                }
            } catch (err) {
                console.error('Poll error:', err);
            }
        }

        setInterval(pollAnnouncements, 500);

        async function send() {
            const input = document.getElementById('message');
            const message = input.value.trim();
            if (!message) return;
            addMessage('user', message);
            input.value = '';
            typing.classList.add('show');
            try {
                const response = await fetch('/send', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });
                const data = await response.json();
                addMessage('ai', data.response);
            } catch (err) {
                addMessage('announce', 'Error: ' + err.message);
            } finally {
                typing.classList.remove('show');
            }
        }
    </script>
</body>
</html>
'''

class WebUi(core.channel.Channel):
    """
    A web-based channel for communicating with the AI through a browser interface.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.announcement_queue = []
        self.announcement_id = 0
        self.main_loop = None

    async def run(self):
        """
        Start the Flask web server to handle HTTP requests.
        """
        core.log("webui", "Starting WebUI")

        self.main_loop = asyncio.get_running_loop()

        global channel_instance
        channel_instance = self

        flask_thread = Thread(target=self._run_flask, daemon=True)
        flask_thread.start()

        host = core.config.get("webui_host", "127.0.0.1")
        port = port=core.config.get("webui_port", 5000)
        core.log("webui", f"WebUI started on {host}:{port}")

        while True:
            await asyncio.sleep(1)

    def _run_flask(self):
        """Run Flask in a separate thread."""
        host = core.config.get("webui_host", "127.0.0.1")
        port = port=core.config.get("webui_port", 5000)
        app.run(host, port, debug=False, use_reloader=False)

    async def announce(self, message: str):
        """
        Handle announcements from the framework and push to web UI.
        """
        core.log("webui channel", f"Announcement: {message}")
        self.announcement_id += 1
        self.announcement_queue.append({
            'id': self.announcement_id,
            'content': message
        })

channel_instance = None

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/poll')
def poll_announcements():
    """
    Return announcements newer than the given ID.
    """
    try:
        last_id = int(request.args.get('id', 0))
    except ValueError:
        last_id = 0

    messages = [msg for msg in channel_instance.announcement_queue if msg['id'] > last_id]
    return jsonify({'messages': messages})

@app.route('/send', methods=['POST'])
def send_message():
    global channel_instance
    data = request.get_json()
    user_message = data.get('message', '')

    future = asyncio.run_coroutine_threadsafe(
        channel_instance.send("user", user_message),
        channel_instance.main_loop
    )
    response = future.result()

    return jsonify({'response': response})
