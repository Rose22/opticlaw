import asyncio
from flask import Flask, render_template_string, request, jsonify, Response, cli
import core
from threading import Thread
import logging
import json

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
    <meta name="theme-color" content="#111111">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="OptiClaw">
    <link rel="manifest" href="/manifest.json">
    <link rel="apple-touch-icon" href="/icon-192.png">

    <title>OptiClaw</title>

    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.11.1/build/styles/github-dark.css">
    <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.11.1/build/highlight.min.js"></script>
    <style>
        :root {
            /* Default dark black theme */
            --bg-primary: #0a0a0a;
            --bg-secondary: #111111;
            --bg-tertiary: #1a1a1a;
            --bg-message-user: linear-gradient(135deg, #3a3a3a 0%, #2d2d2d 100%);
            --bg-message-ai: #1a1a1a;
            --bg-message-announce: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
            --bg-message-command: linear-gradient(135deg, #1a2a1a 0%, #0f1f0f 100%);
            --bg-input: #161616;
            --bg-code: #0a0a0a;
            --border-color: #2a2a2a;
            --border-message: #333333;
            --border-user: #444444;
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0a0;
            --text-muted: #666666;
            --text-code: #d0d0d0;
            --accent: #4ade80;
            --accent-glow: rgba(74, 222, 128, 0.6);
            --error: #f08080;
            --error-bg: linear-gradient(135deg, #3a1a1a 0%, #2a0a0a 100%);
            --error-border: #5a2a2a;
            --important: #dada80;
            --important-bg: linear-gradient(135deg, #3a3a1a 0%, #2a2a0a 100%);
            --important-border: #5a5a2a;
            --info: #80b0d0;
            --info-bg: linear-gradient(135deg, #1a2a3a 0%, #0a1a2a 100%);
            --info-border: #2a4a6a;
            --button-bg: linear-gradient(135deg, #3a3a3a 0%, #2a2a2a 100%);
            --button-hover: linear-gradient(135deg, #444444 0%, #333333 100%);
            --button-stop: linear-gradient(135deg, #5a2a2a 0%, #3a1a1a 100%);
            --scrollbar: #2a2a2a;
            --scrollbar-hover: #3a3a3a;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        html, body {
            height: 100%;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
        }

        .app-container {
            display: flex;
            flex-direction: column;
            height: 100%;
            max-width: 900px;
            margin: 0 auto;
            background: var(--bg-secondary);
            box-shadow: 0 0 40px rgba(0,0,0,0.8);
        }

        header {
            padding: 16px 20px;
            background: linear-gradient(180deg, var(--bg-tertiary) 0%, var(--bg-primary) 100%);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .header-right {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        header h1 {
            font-size: 1.3rem;
            font-weight: 600;
        }

        #settings-btn {
            padding: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        #settings-btn svg {
            width: 16px;
            height: 16px;
        }

        /* Settings Modal */
        .settings-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.2s, visibility 0.2s;
            z-index: 1000;
        }

        .settings-overlay.show {
            opacity: 1;
            visibility: visible;
        }

        .settings-modal {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0.95);
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            width: 90%;
            max-width: 500px;
            max-height: 80vh;
            overflow-y: auto;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.2s, visibility 0.2s, transform 0.2s;
            z-index: 1001;
        }

        .settings-modal.show {
            opacity: 1;
            visibility: visible;
            transform: translate(-50%, -50%) scale(1);
        }

        .settings-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            border-bottom: 1px solid var(--border-color);
        }

        .settings-header h2 {
            font-size: 1.2rem;
            color: var(--text-primary);
        }

        .settings-close {
            background: none;
            border: none;
            font-size: 1.5rem;
            color: var(--text-secondary);
            cursor: pointer;
            padding: 4px 8px;
            border-radius: 4px;
            transition: background 0.2s, color 0.2s;
        }

        .settings-close:hover {
            background: var(--bg-tertiary);
            color: var(--text-primary);
        }

        .settings-content {
            padding: 16px 20px;
        }

        .settings-content h3 {
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .theme-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
            gap: 8px;
        }

        .theme-btn {
            padding: 12px 8px;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            background: var(--bg-tertiary);
            color: var(--text-primary);
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s;
            text-align: center;
        }

        .theme-btn:hover {
            border-color: var(--accent);
            transform: translateY(-2px);
        }

        .theme-btn.active {
            border-color: var(--accent);
            box-shadow: 0 0 10px var(--accent-glow);
        }

        .theme-preview {
            width: 100%;
            height: 24px;
            border-radius: 4px;
            margin-bottom: 6px;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            background: var(--accent);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--accent-glow);
            animation: pulse 2s infinite;
        }

        .status-dot.inactive {
            background: #f87171;
            box-shadow: 0 0 10px rgba(248,113,113,0.6);
        }

        .status-dot.connecting {
            background: #fbbf24;
            box-shadow: 0 0 10px rgba(251,191,36,0.6);
            animation: pulse 1s infinite;
        }
        .status-dot.connected {
            background: #4ade80;
            box-shadow: 0 0 10px rgba(74,222,128,0.6);
        }
        .status-dot.disconnected {
            background: #f87171;
            box-shadow: 0 0 10px rgba(248,113,113,0.6);
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }

        .header-btn {
            padding: 8px 12px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            color: var(--text-secondary);
            font-size: 0.85rem;
            cursor: pointer;
            transition: background 0.2s, color 0.2s;
        }

        .header-btn:hover {
            background: var(--bg-secondary);
            color: var(--text-primary);
        }

        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: var(--bg-primary);
        }

        .message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 16px;
            line-height: 1.5;
            word-wrap: break-word;
            animation: slideIn 0.2s ease-out;
        }
        .message.hidden {
            display: none;
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
            align-self: flex-end;
            background: var(--bg-message-user);
            color: var(--text-primary);
            border: 1px solid var(--border-user);
            border-bottom-right-radius: 4px;
        }

        .message.ai {
            align-self: flex-start;
            background: var(--bg-message-ai);
            border: 1px solid var(--border-message);
            color: var(--text-code);
            border-bottom-left-radius: 4px;
        }

        .message.announce {
            align-self: center;
            background: var(--bg-message-announce);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            font-style: italic;
            text-align: center;
            font-size: 0.9rem;
            max-width: 90%;
        }

        .message.announce.important {
            background: var(--important-bg);
            border: 1px solid var(--important-border);
            color: var(--important);
            font-style: normal;
            font-weight: 500;
        }

        .message.announce.error {
            background: var(--error-bg);
            border: 1px solid var(--error-border);
            color: var(--error);
            font-style: normal;
            font-weight: 500;
        }

        .message.announce.info {
            background: var(--info-bg);
            border: 1px solid var(--info-border);
            color: var(--info);
            font-style: normal;
        }

        .message.command {
            align-self: flex-start;
            background: var(--bg-message-command);
            border: 1px solid #2a4a2a;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9rem;
            border-bottom-left-radius: 4px;
            max-width: 85%;
        }

        .message .timestamp {
            display: block;
            font-size: 0.7rem;
            color: var(--text-muted);
            margin-top: 6px;
            text-align: right;
        }

        .message.ai .timestamp { text-align: left; }
        .message.announce .timestamp { text-align: center; }

        .message pre {
            background: var(--bg-code);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px;
            overflow-x: auto;
            margin: 8px 0;
            position: relative;
        }

        .message code {
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
        }

        .message pre code {
            background: transparent;
            padding: 0;
        }

        .message :not(pre) > code {
            background: var(--bg-tertiary);
            padding: 2px 6px;
            border-radius: 4px;
        }

        .copy-btn {
            position: absolute;
            top: 8px;
            right: 8px;
            padding: 4px 8px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            color: var(--text-secondary);
            font-size: 0.75rem;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.2s, background 0.2s;
        }

        .message pre:hover .copy-btn { opacity: 1; }
        .copy-btn:hover { background: var(--bg-secondary); color: var(--text-primary); }

        .message h1, .message h2, .message h3 {
            margin: 12px 0 8px;
        }

        .message h1 { font-size: 1.4em; }
        .message h2 { font-size: 1.2em; }
        .message h3 { font-size: 1.1em; }

        .message ul, .message ol {
            margin: 8px 0;
            padding-left: 24px;
        }

        .message li {
            margin: 4px 0;
        }

        .message blockquote {
            border-left: 3px solid #4a4a4a;
            margin: 8px 0;
            padding-left: 12px;
        }

        .message a {
            text-decoration: none;
        }

        .message a:hover {
            text-decoration: underline;
        }

        .message table {
            border-collapse: collapse;
            margin: 8px 0;
        }

        .message th, .message td {
            border: 1px solid #3a3a3a;
            padding: 8px 12px;
        }

        .message th {
            background: #1a1a1a;
        }

        .message hr {
            border: none;
            border-top: 1px solid #3a3a3a;
            margin: 12px 0;
        }

        .typing-indicator {
            display: none;
            align-self: flex-start;
            padding: 12px 16px;
            background: var(--bg-message-ai);
            border: 1px solid var(--border-message);
            border-radius: 16px;
            border-bottom-left-radius: 4px;
        }

        .typing-indicator.show { display: flex; gap: 4px; align-items: center; }

        .typing-indicator span {
            width: 8px;
            height: 8px;
            background: var(--text-muted);
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out;
        }

        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0.8); }
            40% { transform: scale(1.2); }
        }

        .input-area {
            padding: 16px;
            background: var(--bg-primary);
            border-top: 1px solid var(--border-color);
            display: flex;
            gap: 12px;
            align-items: center;
            flex-shrink: 0;
        }

        #upload {
            padding: 14px 16px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            color: var(--text-secondary);
            cursor: pointer;
            transition: background 0.2s, color 0.2s, border-color 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }

        #upload:hover {
            background: var(--bg-secondary);
            color: var(--accent);
            border-color: var(--accent);
        }
        #upload svg { width: 20px; height: 20px; }
        #file-input { display: none; }

        #message {
            flex: 1;
            padding: 10px 18px;
            border: 1px solid var(--border-color);
            border-radius: 24px;
            background: var(--bg-input);
            color: var(--text-primary);
            font-size: 1rem;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
            resize: none;
            min-height: 44px;
            max-height: 200px;
            overflow: hidden;
            font-family: inherit;
            line-height: 1.4;
        }

        #message:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-glow);
        }

        #message::placeholder { color: var(--text-muted); }
        #message:disabled { opacity: 0.5; cursor: not-allowed; }

        #send {
            padding: 14px 24px;
            background: var(--button-bg);
            border: 1px solid var(--accent);
            border-radius: 24px;
            color: var(--text-primary);
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.1s, background 0.2s, box-shadow 0.2s;
            flex-shrink: 0;
        }

        #send.hidden { display: none; }
        #send:hover {
            background: var(--button-hover);
            box-shadow: 0 0 15px var(--accent-glow);
        }
        #send:active { transform: scale(0.96); }
        #send:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

        #stop {
            padding: 14px 24px;
            background: var(--error-bg);
            border: 1px solid var(--error-border);
            border-radius: 24px;
            color: var(--error);
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.1s, background 0.2s;
            flex-shrink: 0;
            display: none;
        }

        #stop:hover { 
            background: linear-gradient(135deg, #5a2a2a 0%, #4a1a1a 100%);
            box-shadow: 0 0 15px rgba(248, 113, 113, 0.3);
        }
        #stop:active { transform: scale(0.96); }
        #stop.show { display: block; }

        .chat-container::-webkit-scrollbar { width: 6px; }
        .chat-container::-webkit-scrollbar-track { background: var(--bg-primary); }
        .chat-container::-webkit-scrollbar-thumb { background: var(--scrollbar); border-radius: 3px; }
        .chat-container::-webkit-scrollbar-thumb:hover { background: var(--scrollbar-hover); }

        @media (max-width: 600px) {
            header {
                padding: 12px 16px;
            }

            header h1 {
                font-size: 1.1rem;
            }

            .header-btn {
                padding: 6px 10px;
                font-size: 0.8rem;
            }

            .chat-container {
                padding: 12px;
            }

            .message {
                max-width: 90%;
                padding: 10px 14px;
            }

            .input-area {
                padding: 12px;
                gap: 8px;
            }

            #upload {
                padding: 12px;
            }

            #message {
                padding: 12px 16px;
            }

            #send, #stop {
                padding: 12px 18px;
            }

            .message pre {
                padding: 10px;
                font-size: 0.85rem;
            }

            .copy-btn {
                opacity: 1;
                padding: 6px 10px;
            }
        }

        @media (max-width: 400px) {
            .header-left {
                gap: 8px;
            }

            .status-dot {
                width: 8px;
                height: 8px;
            }

            .message {
                padding: 8px 12px;
                font-size: 0.95rem;
            }

            #send, #stop {
                padding: 12px 14px;
                font-size: 0.9rem;
            }
        }

    </style>
</head>
<body>
    <div class="app-container">
    <header>
        <div class="header-left">
            <div class="status-dot" id="status"></div>
            <h1>AI Chat</h1>
        </div>
        <div class="header-right">
            <button class="header-btn" id="settings-btn" onclick="toggleSettings()">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="3"></circle>
                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                </svg>
            </button>
            <button class="header-btn" onclick="clearChat()">Clear</button>
        </div>
    </header>

    <!-- Settings Modal -->
    <div class="settings-overlay" id="settings-overlay" onclick="closeSettings(event)"></div>
    <div class="settings-modal" id="settings-modal">
        <div class="settings-header">
            <h2>Settings</h2>
            <button class="settings-close" onclick="toggleSettings()">×</button>
        </div>
        <div class="settings-content">
            <h3>Theme</h3>
            <div class="theme-grid" id="theme-grid"></div>
        </div>
    </div>
        <div class="chat-container" id="chat">
            <div class="typing-indicator" id="typing">
                <span></span><span></span><span></span>
            </div>
        </div>
        <div class="input-area">
            <button id="upload" onclick="document.getElementById('file-input').click()">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
                </svg>
            </button>
            <input type="file" id="file-input" onchange="handleFileUpload(event)">
            <textarea id="message" placeholder="Type a message.." onkeydown="handleKeyDown(event)" rows=1></textarea>
            <script>
            document.getElementById('message').addEventListener('input', function() {
                autoResize(this);
            });
            </script>
            <button id="send" onclick="send()">Send</button>
            <button id="stop" onclick="stopGeneration()">Stop</button>
        </div>
    </div>
    <script>
        let lastAnnouncementId = 0;
        const chat = document.getElementById('chat');
        const typing = document.getElementById('typing');
        const inputField = document.getElementById('message');
        const sendBtn = document.getElementById('send');
        const stopBtn = document.getElementById('stop');
        const statusDot = document.getElementById('status');
        let isStreaming = false;
        let currentAiMsg = null;
        let currentController = null;
        let conversationHistory = [];

        // == Connection Monitoring ==
        let isConnected = false;
        let reconnectAttempts = 0;
        let reconnectTimer = null;
        let connectionCheckInterval = null;
        let hasShownReconnecting = false;
        let reconnectingMsgEl = null;

        function updateConnectionStatus(status) {
            const statusDot = document.getElementById('status');
            statusDot.className = 'status-dot ' + status;

            if (status === 'disconnected') {
                sendBtn.disabled = true;
            } else if (status === 'connected') {
                sendBtn.disabled = false;
                reconnectAttempts = 0;
            }
        }

        function removeReconnectingMessage() {
            if (reconnectingMsgEl) {
                reconnectingMsgEl.remove();
                reconnectingMsgEl = null;
            }
            hasShownReconnecting = false;
        }

        async function checkConnection() {
            try {
                const response = await fetch('/poll?id=' + lastAnnouncementId, {
                    method: 'GET',
                    signal: AbortSignal.timeout(3000)
                });

                if (response.ok) {
                    const wasReconnecting = hasShownReconnecting && !isConnected;

                    if (!isConnected) {
                        isConnected = true;
                        updateConnectionStatus('connected');

                        removeReconnectingMessage();

                        // Show reconnected message only if we were actually reconnecting
                        if (wasReconnecting || reconnectAttempts > 0) {
                            addAnnouncement('Reconnected to server', false, false, true);
                        }
                    }
                } else {
                    throw new Error('Server error');
                }
            } catch (err) {
                const wasConnected = isConnected;

                if (isConnected) {
                    isConnected = false;
                    updateConnectionStatus('disconnected');
                    removeReconnectingMessage();
                    addAnnouncement('Disconnected from server. Reconnecting...', false, false, true);
                    scheduleReconnect();
                } else if (!hasShownReconnecting) {
                    // Not connected and haven't shown reconnecting message yet
                    scheduleReconnect();
                }
            }
        }

        function scheduleReconnect() {
            if (reconnectTimer) clearTimeout(reconnectTimer);

            reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(1.5, Math.min(reconnectAttempts, 10)), 30000);

            updateConnectionStatus('connecting');

            // Show reconnecting message only once
            if (!hasShownReconnecting) {
                hasShownReconnecting = true;
                reconnectingMsgEl = addAnnouncement('Reconnecting...', "info");
                if (reconnectingMsgEl) {
                    reconnectingMsgEl.classList.add('reconnecting');
                }
            }

            reconnectTimer = setTimeout(async () => {
                await checkConnection();
                if (!isConnected) {
                    scheduleReconnect();
                }
            }, delay);
        }


        marked.setOptions({
            breaks: true,
            gfm: true
        });

        function renderMarkdown(text) {
            let html = marked.parse(text);
            return html;
        }

        function highlightCode(element) {
            if (typeof hljs === 'undefined') return;
            element.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);

                const pre = block.parentElement;
                if (!pre.querySelector('.copy-btn')) {
                    const btn = document.createElement('button');
                    btn.className = 'copy-btn';
                    btn.textContent = 'Copy';
                    btn.onclick = () => {
                        navigator.clipboard.writeText(block.textContent).then(() => {
                            btn.textContent = 'Copied!';
                            setTimeout(() => btn.textContent = 'Copy', 1500);
                        });
                    };
                    pre.style.position = 'relative';
                    pre.appendChild(btn);
                }
            });
        }

        function saveHistory() {
            localStorage.setItem('chatHistory', JSON.stringify(conversationHistory));
        }

        function loadHistory() {
            const saved = localStorage.getItem('chatHistory');
            if (saved) {
                conversationHistory = JSON.parse(saved);
                conversationHistory.forEach(msg => {
                    createMessageElement(msg.role, msg.content, msg.timestamp);
                });
            }
        }

        function formatTime(date) {
            if (date) return date;
            return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }

        function createMessageElement(role, content, timestamp) {
            const div = document.createElement('div');
            div.className = 'message ' + role;
            const timeStr = timestamp || formatTime();

            if (role === 'ai' || role === 'user' ) {
                div.innerHTML = renderMarkdown(content);
                highlightCode(div);
            } else {
                div.innerText = content;
            }

            const ts = document.createElement('span');
            ts.className = 'timestamp';
            ts.textContent = timeStr;
            div.appendChild(ts);

            chat.insertBefore(div, typing);
            scrollToBottomDelayed();
            return div;
        }

        function addMessage(role, content, withTimestamp = true, timestamp = null) {
            const timeStr = timestamp || formatTime();
            const msg = { role: role, content: content, timestamp: timeStr };

            if (isStreaming && currentAiMsg && role === 'announce') {
                conversationHistory.push(msg);
                saveHistory();
                chat.insertBefore(createMessageElement(role, content, timeStr), currentAiMsg);
            } else {
                if (role !== 'announce') {
                    conversationHistory.push(msg);
                    saveHistory();
                }
                createMessageElement(role, content, timeStr);
            }
            scrollToBottom();
        }

        function scrollToBottom() {
            requestAnimationFrame(() => {
                chat.scrollTop = chat.scrollHeight;
            });
        }

        // Use a more aggressive scroll for streaming
        function scrollToBottomDelayed() {
            setTimeout(() => {
                requestAnimationFrame(() => {
                    chat.scrollTop = chat.scrollHeight;
                });
            }, 10);
        }

        function setInputState(disabled, showTyping = false, showStop = false) {
            inputField.disabled = false;
            sendBtn.disabled = disabled;
            statusDot.classList.toggle('inactive', disabled);

            if (showTyping) {
                typing.classList.add('show');
            } else {
                typing.classList.remove('show');
            }

            if (showStop) {
                sendBtn.classList.add('hidden');
                stopBtn.classList.add('show');
            } else {
                sendBtn.classList.remove('hidden');
                stopBtn.classList.remove('show');
            }
        }

        function handleKeyDown(event) {
            // Check if we're on mobile
            const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

            if (!isMobile) {
                // Desktop: Enter sends, Shift+Enter adds newline
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    send();
                }
            }
            // Mobile: Enter always adds newline, user clicks Send button
        }

        function autoResize(textarea) {
            if (!textarea.value) {
                textarea.style.height = '44px';
            } else {
                textarea.style.height = 'auto';
                textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
            }
        }
        function clearInput() {
            inputField.value = '';
            autoResize(inputField);
        }

        async function stopGeneration() {
            // Stop the frontend stream first
            if (currentController) {
                currentController.abort();
                currentController = null;
            }

            // Cancel the backend stream
            if (currentStreamId) {
                try {
                    await fetch('/cancel', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({id: currentStreamId})
                    });
                } catch (e) {}
                currentStreamId = null;
            }

            // Show stopped in UI
            if (currentAiMsg) {
                currentAiMsg.classList.remove('hidden');

                let existingContent = currentAiMsg.innerText || '';
                existingContent = existingContent.replace(/\s*\d{1,2}:\d{2}\s*(?:AM|PM)?\s*$/i, '').trim();

                if (existingContent) {
                    currentAiMsg.innerHTML = renderMarkdown(existingContent) + ' <span style="color:#f88;">[Stopped]</span>';
                } else {
                    currentAiMsg.innerHTML = '<span style="color:#f88;">[Stopped]</span>';
                }

                const ts = document.createElement('span');
                ts.className = 'timestamp';
                ts.textContent = formatTime();
                currentAiMsg.appendChild(ts);

                const finalContent = existingContent ? existingContent + ' [Stopped]' : '[Stopped]';
                conversationHistory.push({ role: 'ai', content: finalContent, timestamp: formatTime() });
                saveHistory();

                currentAiMsg = null;
            }

            // Send /stop WITHOUT awaiting - let it run in background
            fetch('/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: '/stop'})
            }).catch(e => {});

            setInputState(false, false, false);
            isStreaming = false;
            inputField.focus();
        }

        function clearChatUI() {
            conversationHistory = [];
            saveHistory();
            const messages = chat.querySelectorAll('.message');
            messages.forEach(msg => msg.remove());
            currentAiMsg = null;
        }

        function clearChat() {
            clearChatUI();
            sendCommand('/new');
        }

        async function sendCommand(cmd) {
            // Stop any ongoing stream first
            if (isStreaming) {
                await stopGeneration();
            }

            if (cmd.startsWith("/new")) {
                clearChatUI();
            }
            if (cmd.startsWith("/stop")) {
                await stopGeneration();
                return;
            }

            const timestamp = formatTime();
            conversationHistory.push({ role: 'user', content: cmd, timestamp: timestamp });
            saveHistory();
            createMessageElement('user', cmd, timestamp);

            try {
                const response = await fetch('/send', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: cmd})
                });

                const data = await response.json();
                if (data.response) {
                    const ts = formatTime();
                    const msg = { role: 'command', content: data.response, timestamp: ts };
                    conversationHistory.push(msg);
                    saveHistory();
                    createMessageElement('command', data.response, ts);
                }
            } catch (err) {
                if (cmd.startsWith("/restart")) {
                    // lol just ignore the error cuz server restarting n stuff
                    clearChatUI();

                    const timestamp = formatTime();
                    conversationHistory.push({ role: 'command', content: "restarting server", timestamp: timestamp });
                    saveHistory();
                    createMessageElement('command', "restarting server..", timestamp);

                    return;
                }
                addMessage('announce', 'Error: ' + err.message);
            }
            inputField.focus();
        }

        async function pollAnnouncements() {
            if (!isConnected) return;

            try {
                const response = await fetch('/poll?id=' + lastAnnouncementId, {
                    signal: AbortSignal.timeout(5000)
                });

                if (!response.ok) throw new Error('Poll failed');

                const data = await response.json();
                if (data.messages) {
                    for (const msg of data.messages) {
                        addAnnouncement(msg.content, msg.type);
                        lastAnnouncementId = msg.id;
                    }
                }
            } catch (err) {
                console.error('Poll error:', err);
                isConnected = false;
                updateConnectionStatus('disconnected');
                addAnnouncement('Disconnected from server. Reconnecting...', "info");
                scheduleReconnect();
            }
        }

        function addAnnouncement(content, type = null) {
            const div = document.createElement('div');
            div.className = 'message announce';
            if (type) div.classList.add(type);

            const timeStr = formatTime();
            div.innerHTML = content + '<span class="timestamp">' + timeStr + '</span>';

            if (isStreaming && currentAiMsg) {
                chat.insertBefore(div, currentAiMsg);
            } else {
                chat.insertBefore(div, typing);
            }
            scrollToBottom();
        }

        setInterval(() => {
            if (isConnected) pollAnnouncements();
        }, 500);

        async function send() {
            if (!isConnected) {
                addAnnouncement('Cannot send message - not connected to server', "error");
                return;
            }

            const message = inputField.value.trim();
            if (!message) return;

            if (message.startsWith('/')) {
                clearInput();
                await sendCommand(message);
                return;
            }
            if (isStreaming) return;

            clearInput();

            const timestamp = formatTime();
            addMessage('user', message);

            setInputState(true, true, true);
            isStreaming = true;

            currentController = new AbortController();

            const aiMsg = document.createElement('div');
            aiMsg.className = 'message ai hidden';
            chat.insertBefore(aiMsg, typing);
            currentAiMsg = aiMsg;

            let aiContent = '';
            let streamStarted = false;

            try {
                const response = await fetch('/stream', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message}),
                    signal: currentController.signal
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\\n');
                    buffer = lines.pop() || '';

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                if (data.id) {
                                    currentStreamId = data.id;
                                }
                                if (data.cancelled) {
                                    aiMsg.innerHTML = '<span style="color:#f88;">[Cancelled]</span>';
                                    const ts = document.createElement('span');
                                    ts.className = 'timestamp';
                                    ts.textContent = formatTime();
                                    aiMsg.appendChild(ts);
                                    setInputState(false, false, false);
                                    isStreaming = false;
                                    currentAiMsg = null;
                                    currentStreamId = null;
                                    return;  // Exit early
                                }
                                if (data.token) {
                                    if (!streamStarted) {
                                        streamStarted = true;
                                        typing.classList.remove('show');
                                        aiMsg.classList.remove('hidden');
                                    }
                                    aiContent += data.token;
                                    aiMsg.innerHTML = renderMarkdown(aiContent);
                                    highlightCode(aiMsg);
                                    const ts = aiMsg.querySelector('.timestamp');
                                    if (!ts) {
                                        const tsEl = document.createElement('span');
                                        tsEl.className = 'timestamp';
                                        aiMsg.appendChild(tsEl);
                                    }
                                    scrollToBottomDelayed();
                                }
                                if (data.done) {
                                    aiMsg.innerHTML = renderMarkdown(aiContent);
                                    highlightCode(aiMsg);
                                    const ts = document.createElement('span');
                                    ts.className = 'timestamp';
                                    ts.textContent = formatTime();
                                    aiMsg.appendChild(ts);
                                    conversationHistory.push({ role: 'ai', content: aiContent, timestamp: formatTime() });
                                    saveHistory();
                                }
                                if (data.error) {
                                    if (!streamStarted) {
                                        aiMsg.classList.remove('hidden');
                                    }
                                    aiMsg.innerHTML = '<span style="color:#f88;">[Error: ' + data.error + ']</span>';
                                    const ts = document.createElement('span');
                                    ts.className = 'timestamp';
                                    ts.textContent = formatTime();
                                    aiMsg.appendChild(ts);
                                }
                            } catch (e) { /* ignore parse errors */ }
                        }
                    }
                }
            } catch (err) {
                if (err.name === 'AbortError') {
                    // User stopped - already handled in stopGeneration()
                } else {
                    if (!streamStarted) {
                        aiMsg.classList.remove('hidden');
                    }
                    aiMsg.innerHTML = '<span style="color:#f88;">Error: ' + err.message + '</span>';
                    const ts = document.createElement('span');
                    ts.className = 'timestamp';
                    ts.textContent = formatTime();
                    aiMsg.appendChild(ts);
                }
            } finally {
                setInputState(false, false, false);
                isStreaming = false;
                currentController = null;
                currentAiMsg = null;
                inputField.focus();
            }
        }

        async function handleFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            // Reset file input
            event.target.value = '';

            // Show uploading message
            const timestamp = formatTime();
            const uploadMsg = `[Uploading: ${file.name}]`;
            addMessage('announce', uploadMsg);

            try {
                // Read file as base64
                const reader = new FileReader();
                const base64 = await new Promise((resolve, reject) => {
                    reader.onload = () => resolve(reader.result.split(',')[1]);
                    reader.onerror = reject;
                    reader.readAsDataURL(file);
                });

                // Send to backend
                const response = await fetch('/upload', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        filename: file.name,
                        content: base64,
                        mimetype: file.type
                    })
                });

                const data = await response.json();

                if (data.success) {
                    const ts = formatTime();
                    conversationHistory.push({ role: 'user', content: `[Uploaded: ${file.name}]`, timestamp: ts });
                    saveHistory();
                    createMessageElement('user', `[Uploaded: ${file.name}]`, ts);

                    if (data.message) {
                        addMessage('announce', data.message);
                    }
                } else {
                    addMessage('announce', 'Error: ' + (data.error || 'Upload failed'));
                }
            } catch (err) {
                addMessage('announce', 'Error: ' + err.message);
            }

            inputField.focus();
        }

    </script>

    <script>
        // == Themes! ==
        // Theme definitions
const themes = {
        'dark-black': {
            name: 'Black',
            mode: 'dark',
            vars: {
                '--bg-primary': '#0a0a0a',
                '--bg-secondary': '#111111',
                '--bg-tertiary': '#1a1a1a',
                '--bg-message-user': 'linear-gradient(135deg, #3a3a3a 0%, #2d2d2d 100%)',
                '--bg-message-ai': '#1a1a1a',
                '--bg-message-announce': 'linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #1a2a1a 0%, #0f1f0f 100%)',
                '--bg-input': '#161616',
                '--bg-code': '#0a0a0a',
                '--border-color': '#2a2a2a',
                '--border-message': '#333333',
                '--border-user': '#444444',
                '--text-primary': '#e0e0e0',
                '--text-secondary': '#a0a0a0',
                '--text-muted': '#666666',
                '--text-code': '#d0d0d0',
                '--accent': '#555555',
                '--accent-glow': 'rgba(255, 255, 255, 0.3)',
                '--error': '#f08080',
                '--error-bg': 'linear-gradient(135deg, #3a1a1a 0%, #2a0a0a 100%)',
                '--error-border': '#5a2a2a',
                '--important': '#dada80',
                '--important-bg': 'linear-gradient(135deg, #3a3a1a 0%, #2a2a0a 100%)',
                '--important-border': '#5a5a2a',
                '--info': '#80b0d0',
                '--info-bg': 'linear-gradient(135deg, #1a2a3a 0%, #0a1a2a 100%)',
                '--info-border': '#2a4a6a',
                '--button-bg': 'linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%)',
                '--button-hover': 'linear-gradient(135deg, #3a3a3a 0%, #2a2a2a 100%)',
                '--button-stop': 'linear-gradient(135deg, #5a2a2a 0%, #3a1a1a 100%)',
                '--scrollbar': '#2a2a2a',
                '--scrollbar-hover': '#3a3a3a'
            }
        },
        'dark-gray': {
            name: 'Gray',
            mode: 'dark',
            vars: {
                '--bg-primary': '#1a1a1a',
                '--bg-secondary': '#242424',
                '--bg-tertiary': '#2e2e2e',
                '--bg-message-user': 'linear-gradient(135deg, #404040 0%, #363636 100%)',
                '--bg-message-ai': '#2e2e2e',
                '--bg-message-announce': 'linear-gradient(135deg, #383838 0%, #2e2e2e 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #2e382e 0%, #243024 100%)',
                '--bg-input': '#2a2a2a',
                '--bg-code': '#1a1a1a',
                '--border-color': '#404040',
                '--border-message': '#484848',
                '--border-user': '#505050',
                '--text-primary': '#f0f0f0',
                '--text-secondary': '#b0b0b0',
                '--text-muted': '#808080',
                '--text-code': '#e0e0e0',
                '--accent': '#60a0f0',
                '--accent-glow': 'rgba(96, 160, 240, 0.4)',
                '--error': '#f08080',
                '--error-bg': 'linear-gradient(135deg, #3a1a1a 0%, #2a0a0a 100%)',
                '--error-border': '#5a2a2a',
                '--important': '#dada80',
                '--important-bg': 'linear-gradient(135deg, #3a3a1a 0%, #2a2a0a 100%)',
                '--important-border': '#5a5a2a',
                '--info': '#80b0d0',
                '--info-bg': 'linear-gradient(135deg, #1a2a3a 0%, #0a1a2a 100%)',
                '--info-border': '#2a4a6a',
                '--button-bg': 'linear-gradient(135deg, #404040 0%, #303030 100%)',
                '--button-hover': 'linear-gradient(135deg, #505050 0%, #404040 100%)',
                '--button-stop': 'linear-gradient(135deg, #5a2a2a 0%, #3a1a1a 100%)',
                '--scrollbar': '#404040',
                '--scrollbar-hover': '#505050'
            }
        },
        'dark-pink': {
            name: 'Pink',
            mode: 'dark',
            vars: {
                '--bg-primary': '#1a0a14',
                '--bg-secondary': '#24101c',
                '--bg-tertiary': '#2e1828',
                '--bg-message-user': 'linear-gradient(135deg, #482838 0%, #3a2030 100%)',
                '--bg-message-ai': '#2e1828',
                '--bg-message-announce': 'linear-gradient(135deg, #382030 0%, #2e1828 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #283028 0%, #202820 100%)',
                '--bg-input': '#201018',
                '--bg-code': '#1a0a14',
                '--border-color': '#482840',
                '--border-message': '#503048',
                '--border-user': '#583850',
                '--text-primary': '#f0d0e0',
                '--text-secondary': '#c090a8',
                '--text-muted': '#886878',
                '--text-code': '#e0b8d0',
                '--accent': '#f060a0',
                '--accent-glow': 'rgba(240, 96, 160, 0.4)',
                '--error': '#f08080',
                '--error-bg': 'linear-gradient(135deg, #3a1a1a 0%, #2a0a0a 100%)',
                '--error-border': '#5a2a2a',
                '--important': '#dada80',
                '--important-bg': 'linear-gradient(135deg, #3a3a1a 0%, #2a2a0a 100%)',
                '--important-border': '#5a5a2a',
                '--info': '#80b0d0',
                '--info-bg': 'linear-gradient(135deg, #1a2a3a 0%, #0a1a2a 100%)',
                '--info-border': '#2a4a6a',
                '--button-bg': 'linear-gradient(135deg, #482838 0%, #382030 100%)',
                '--button-hover': 'linear-gradient(135deg, #583848 0%, #482838 100%)',
                '--button-stop': 'linear-gradient(135deg, #5a2a2a 0%, #3a1a1a 100%)',
                '--scrollbar': '#482840',
                '--scrollbar-hover': '#583850'
            }
        },
        'dark-magenta': {
            name: 'Magenta',
            mode: 'dark',
            vars: {
                '--bg-primary': '#140a18',
                '--bg-secondary': '#201024',
                '--bg-tertiary': '#2c1830',
                '--bg-message-user': 'linear-gradient(135deg, #482850 0%, #3a2040 100%)',
                '--bg-message-ai': '#2c1830',
                '--bg-message-announce': 'linear-gradient(135deg, #382038 0%, #2c1830 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #283028 0%, #202820 100%)',
                '--bg-input': '#1c101e',
                '--bg-code': '#140a18',
                '--border-color': '#482850',
                '--border-message': '#503058',
                '--border-user': '#583860',
                '--text-primary': '#f0d0f0',
                '--text-secondary': '#c898c8',
                '--text-muted': '#906890',
                '--text-code': '#e0b0e0',
                '--accent': '#c060d0',
                '--accent-glow': 'rgba(192, 96, 208, 0.4)',
                '--error': '#f08080',
                '--error-bg': 'linear-gradient(135deg, #3a1a1a 0%, #2a0a0a 100%)',
                '--error-border': '#5a2a2a',
                '--important': '#dada80',
                '--important-bg': 'linear-gradient(135deg, #3a3a1a 0%, #2a2a0a 100%)',
                '--important-border': '#5a5a2a',
                '--info': '#80b0d0',
                '--info-bg': 'linear-gradient(135deg, #1a2a3a 0%, #0a1a2a 100%)',
                '--info-border': '#2a4a6a',
                '--button-bg': 'linear-gradient(135deg, #482850 0%, #382040 100%)',
                '--button-hover': 'linear-gradient(135deg, #583860 0%, #482850 100%)',
                '--button-stop': 'linear-gradient(135deg, #5a2a2a 0%, #3a1a1a 100%)',
                '--scrollbar': '#482850',
                '--scrollbar-hover': '#583860'
            }
        },
        'dark-violet': {
            name: 'Violet',
            mode: 'dark',
            vars: {
                '--bg-primary': '#100a18',
                '--bg-secondary': '#1a1028',
                '--bg-tertiary': '#241836',
                '--bg-message-user': 'linear-gradient(135deg, #402860 0%, #342050 100%)',
                '--bg-message-ai': '#241836',
                '--bg-message-announce': 'linear-gradient(135deg, #302048 0%, #241836 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #203028 0%, #182820 100%)',
                '--bg-input': '#180e24',
                '--bg-code': '#100a18',
                '--border-color': '#403060',
                '--border-message': '#483868',
                '--border-user': '#504070',
                '--text-primary': '#e8d0f8',
                '--text-secondary': '#b898d0',
                '--text-muted': '#8068a0',
                '--text-code': '#d8b0f0',
                '--accent': '#9060e0',
                '--accent-glow': 'rgba(144, 96, 224, 0.4)',
                '--error': '#f08080',
                '--error-bg': 'linear-gradient(135deg, #3a1a1a 0%, #2a0a0a 100%)',
                '--error-border': '#5a2a2a',
                '--important': '#dada80',
                '--important-bg': 'linear-gradient(135deg, #3a3a1a 0%, #2a2a0a 100%)',
                '--important-border': '#5a5a2a',
                '--info': '#80b0d0',
                '--info-bg': 'linear-gradient(135deg, #1a2a3a 0%, #0a1a2a 100%)',
                '--info-border': '#2a4a6a',
                '--button-bg': 'linear-gradient(135deg, #402860 0%, #302050 100%)',
                '--button-hover': 'linear-gradient(135deg, #503870 0%, #402860 100%)',
                '--button-stop': 'linear-gradient(135deg, #5a2a2a 0%, #3a1a1a 100%)',
                '--scrollbar': '#403060',
                '--scrollbar-hover': '#504070'
            }
        },
        'dark-purple': {
            name: 'Purple',
            mode: 'dark',
            vars: {
                '--bg-primary': '#0e0a14',
                '--bg-secondary': '#18101e',
                '--bg-tertiary': '#221828',
                '--bg-message-user': 'linear-gradient(135deg, #382850 0%, #2c2040 100%)',
                '--bg-message-ai': '#221828',
                '--bg-message-announce': 'linear-gradient(135deg, #282038 0%, #221828 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #182820 0%, #142018 100%)',
                '--bg-input': '#140e1a',
                '--bg-code': '#0e0a14',
                '--border-color': '#382850',
                '--border-message': '#403058',
                '--border-user': '#483860',
                '--text-primary': '#e0d0f0',
                '--text-secondary': '#b090c8',
                '--text-muted': '#785898',
                '--text-code': '#d0a8e8',
                '--accent': '#9858d8',
                '--accent-glow': 'rgba(152, 88, 216, 0.4)',
                '--error': '#f08080',
                '--error-bg': 'linear-gradient(135deg, #3a1a1a 0%, #2a0a0a 100%)',
                '--error-border': '#5a2a2a',
                '--important': '#dada80',
                '--important-bg': 'linear-gradient(135deg, #3a3a1a 0%, #2a2a0a 100%)',
                '--important-border': '#5a5a2a',
                '--info': '#80b0d0',
                '--info-bg': 'linear-gradient(135deg, #1a2a3a 0%, #0a1a2a 100%)',
                '--info-border': '#2a4a6a',
                '--button-bg': 'linear-gradient(135deg, #382850 0%, #282040 100%)',
                '--button-hover': 'linear-gradient(135deg, #483860 0%, #382850 100%)',
                '--button-stop': 'linear-gradient(135deg, #5a2a2a 0%, #3a1a1a 100%)',
                '--scrollbar': '#382850',
                '--scrollbar-hover': '#483860'
            }
        },
        'dark-blue': {
            name: 'Blue',
            mode: 'dark',
            vars: {
                '--bg-primary': '#0a0e14',
                '--bg-secondary': '#101820',
                '--bg-tertiary': '#182430',
                '--bg-message-user': 'linear-gradient(135deg, #283850 0%, #203038 100%)',
                '--bg-message-ai': '#182430',
                '--bg-message-announce': 'linear-gradient(135deg, #203040 0%, #182430 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #183020 0%, #142818 100%)',
                '--bg-input': '#0c1218',
                '--bg-code': '#0a0e14',
                '--border-color': '#283850',
                '--border-message': '#304060',
                '--border-user': '#384868',
                '--text-primary': '#d0e0f0',
                '--text-secondary': '#90b0d0',
                '--text-muted': '#5878a0',
                '--text-code': '#b0d0f0',
                '--accent': '#4090e0',
                '--accent-glow': 'rgba(64, 144, 224, 0.4)',
                '--error': '#f08080',
                '--error-bg': 'linear-gradient(135deg, #3a1a1a 0%, #2a0a0a 100%)',
                '--error-border': '#5a2a2a',
                '--important': '#dada80',
                '--important-bg': 'linear-gradient(135deg, #3a3a1a 0%, #2a2a0a 100%)',
                '--important-border': '#5a5a2a',
                '--info': '#80b0d0',
                '--info-bg': 'linear-gradient(135deg, #1a2a3a 0%, #0a1a2a 100%)',
                '--info-border': '#2a4a6a',
                '--button-bg': 'linear-gradient(135deg, #283850 0%, #183038 100%)',
                '--button-hover': 'linear-gradient(135deg, #384860 0%, #283850 100%)',
                '--button-stop': 'linear-gradient(135deg, #5a2a2a 0%, #3a1a1a 100%)',
                '--scrollbar': '#283850',
                '--scrollbar-hover': '#384860'
            }
        },
        'dark-green': {
            name: 'Green',
            mode: 'dark',
            vars: {
                '--bg-primary': '#0a140e',
                '--bg-secondary': '#101c14',
                '--bg-tertiary': '#182820',
                '--bg-message-user': 'linear-gradient(135deg, #284038 0%, #1c3828 100%)',
                '--bg-message-ai': '#182820',
                '--bg-message-announce': 'linear-gradient(135deg, #204030 0%, #183020 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #283820 0%, #1c2818 100%)',
                '--bg-input': '#0c140e',
                '--bg-code': '#0a140e',
                '--border-color': '#284030',
                '--border-message': '#305038',
                '--border-user': '#385840',
                '--text-primary': '#c8e8d0',
                '--text-secondary': '#80c090',
                '--text-muted': '#487058',
                '--text-code': '#a8e0b8',
                '--accent': '#50c870',
                '--accent-glow': 'rgba(80, 200, 112, 0.4)',
                '--error': '#f08080',
                '--error-bg': 'linear-gradient(135deg, #3a1a1a 0%, #2a0a0a 100%)',
                '--error-border': '#5a2a2a',
                '--important': '#dada80',
                '--important-bg': 'linear-gradient(135deg, #3a3a1a 0%, #2a2a0a 100%)',
                '--important-border': '#5a5a2a',
                '--info': '#80b0d0',
                '--info-bg': 'linear-gradient(135deg, #1a2a3a 0%, #0a1a2a 100%)',
                '--info-border': '#2a4a6a',
                '--button-bg': 'linear-gradient(135deg, #284038 0%, #183828 100%)',
                '--button-hover': 'linear-gradient(135deg, #385048 0%, #284038 100%)',
                '--button-stop': 'linear-gradient(135deg, #5a2a2a 0%, #3a1a1a 100%)',
                '--scrollbar': '#284030',
                '--scrollbar-hover': '#385038'
            }
        },
        'dark-red': {
            name: 'Red',
            mode: 'dark',
            vars: {
                '--bg-primary': '#14100e',
                '--bg-secondary': '#201814',
                '--bg-tertiary': '#2e2018',
                '--bg-message-user': 'linear-gradient(135deg, #503028 0%, #442820 100%)',
                '--bg-message-ai': '#2e2018',
                '--bg-message-announce': 'linear-gradient(135deg, #403028 0%, #302018 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #304028 0%, #243020 100%)',
                '--bg-input': '#1a100e',
                '--bg-code': '#14100e',
                '--border-color': '#503828',
                '--border-message': '#584030',
                '--border-user': '#604838',
                '--text-primary': '#f0d8d0',
                '--text-secondary': '#c89080',
                '--text-muted': '#905850',
                '--text-code': '#e8b8a8',
                '--accent': '#e06050',
                '--accent-glow': 'rgba(224, 96, 80, 0.4)',
                '--error': '#f08080',
                '--error-bg': 'linear-gradient(135deg, #3a1a1a 0%, #2a0a0a 100%)',
                '--error-border': '#5a2a2a',
                '--important': '#dada80',
                '--important-bg': 'linear-gradient(135deg, #3a3a1a 0%, #2a2a0a 100%)',
                '--important-border': '#5a5a2a',
                '--info': '#80b0d0',
                '--info-bg': 'linear-gradient(135deg, #1a2a3a 0%, #0a1a2a 100%)',
                '--info-border': '#2a4a6a',
                '--button-bg': 'linear-gradient(135deg, #503028 0%, #402820 100%)',
                '--button-hover': 'linear-gradient(135deg, #604038 0%, #503028 100%)',
                '--button-stop': 'linear-gradient(135deg, #5a2a2a 0%, #3a1a1a 100%)',
                '--scrollbar': '#503828',
                '--scrollbar-hover': '#604838'
            }
        },
        'dark-sepia': {
            name: 'Sepia',
            mode: 'dark',
            vars: {
                '--bg-primary': '#1a1510',
                '--bg-secondary': '#242018',
                '--bg-tertiary': '#302820',
                '--bg-message-user': 'linear-gradient(135deg, #483828 0%, #3c3020 100%)',
                '--bg-message-ai': '#302820',
                '--bg-message-announce': 'linear-gradient(135deg, #403020 0%, #302818 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #304828 0%, #243820 100%)',
                '--bg-input': '#20180c',
                '--bg-code': '#1a1510',
                '--border-color': '#483820',
                '--border-message': '#504028',
                '--border-user': '#584830',
                '--text-primary': '#f0e0d0',
                '--text-secondary': '#c8a878',
                '--text-muted': '#907850',
                '--text-code': '#e8d0b8',
                '--accent': '#c09050',
                '--accent-glow': 'rgba(192, 144, 80, 0.4)',
                '--error': '#f08080',
                '--error-bg': 'linear-gradient(135deg, #3a1a1a 0%, #2a0a0a 100%)',
                '--error-border': '#5a2a2a',
                '--important': '#dada80',
                '--important-bg': 'linear-gradient(135deg, #3a3a1a 0%, #2a2a0a 100%)',
                '--important-border': '#5a5a2a',
                '--info': '#80b0d0',
                '--info-bg': 'linear-gradient(135deg, #1a2a3a 0%, #0a1a2a 100%)',
                '--info-border': '#2a4a6a',
                '--button-bg': 'linear-gradient(135deg, #483828 0%, #383020 100%)',
                '--button-hover': 'linear-gradient(135deg, #584838 0%, #483828 100%)',
                '--button-stop': 'linear-gradient(135deg, #5a2a2a 0%, #3a1a1a 100%)',
                '--scrollbar': '#483820',
                '--scrollbar-hover': '#584830'
            }
        },
        'dark-silver': {
            name: 'Silver',
            mode: 'dark',
            vars: {
                '--bg-primary': '#18181c',
                '--bg-secondary': '#222228',
                '--bg-tertiary': '#2e2e36',
                '--bg-message-user': 'linear-gradient(135deg, #4a4a56 0%, #3e3e48 100%)',
                '--bg-message-ai': '#2e2e36',
                '--bg-message-announce': 'linear-gradient(135deg, #3a3a44 0%, #2e2e36 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #324034 0%, #28342a 100%)',
                '--bg-input': '#201f24',
                '--bg-code': '#18181c',
                '--border-color': '#484854',
                '--border-message': '#525260',
                '--border-user': '#5c5c6a',
                '--text-primary': '#e8e8f0',
                '--text-secondary': '#b0b0c0',
                '--text-muted': '#787890',
                '--text-code': '#d0d0e0',
                '--accent': '#8088a0',
                '--accent-glow': 'rgba(128, 136, 160, 0.4)',
                '--error': '#f08080',
                '--error-bg': 'linear-gradient(135deg, #3a1a1a 0%, #2a0a0a 100%)',
                '--error-border': '#5a2a2a',
                '--important': '#dada80',
                '--important-bg': 'linear-gradient(135deg, #3a3a1a 0%, #2a2a0a 100%)',
                '--important-border': '#5a5a2a',
                '--info': '#80b0d0',
                '--info-bg': 'linear-gradient(135deg, #1a2a3a 0%, #0a1a2a 100%)',
                '--info-border': '#2a4a6a',
                '--button-bg': 'linear-gradient(135deg, #4a4a56 0%, #3a3a46 100%)',
                '--button-hover': 'linear-gradient(135deg, #5a5a66 0%, #4a4a56 100%)',
                '--button-stop': 'linear-gradient(135deg, #5a2a2a 0%, #3a1a1a 100%)',
                '--scrollbar': '#484854',
                '--scrollbar-hover': '#585864'
            }
        },
        'dark-gold': {
            name: 'Gold',
            mode: 'dark',
            vars: {
                '--bg-primary': '#141210',
                '--bg-secondary': '#201c18',
                '--bg-tertiary': '#2c2820',
                '--bg-message-user': 'linear-gradient(135deg, #484028 0%, #3c3820 100%)',
                '--bg-message-ai': '#2c2820',
                '--bg-message-announce': 'linear-gradient(135deg, #403828 0%, #2c2818 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #284030 0%, #203828 100%)',
                '--bg-input': '#1c1810',
                '--bg-code': '#141210',
                '--border-color': '#584830',
                '--border-message': '#605038',
                '--border-user': '#685840',
                '--text-primary': '#f0e8c8',
                '--text-secondary': '#c8b878',
                '--text-muted': '#907848',
                '--text-code': '#e8d8a0',
                '--accent': '#d0a040',
                '--accent-glow': 'rgba(208, 160, 64, 0.4)',
                '--error': '#f08080',
                '--error-bg': 'linear-gradient(135deg, #3a1a1a 0%, #2a0a0a 100%)',
                '--error-border': '#5a2a2a',
                '--important': '#dada80',
                '--important-bg': 'linear-gradient(135deg, #3a3a1a 0%, #2a2a0a 100%)',
                '--important-border': '#5a5a2a',
                '--info': '#80b0d0',
                '--info-bg': 'linear-gradient(135deg, #1a2a3a 0%, #0a1a2a 100%)',
                '--info-border': '#2a4a6a',
                '--button-bg': 'linear-gradient(135deg, #484028 0%, #3c3820 100%)',
                '--button-hover': 'linear-gradient(135deg, #585038 0%, #484028 100%)',
                '--button-stop': 'linear-gradient(135deg, #5a2a2a 0%, #3a1a1a 100%)',
                '--scrollbar': '#584830',
                '--scrollbar-hover': '#685840'
            }
        },
        'dark-rosegold': {
            name: 'Rose Gold',
            mode: 'dark',
            vars: {
                '--bg-primary': '#18120e',
                '--bg-secondary': '#221a16',
                '--bg-tertiary': '#302420',
                '--bg-message-user': 'linear-gradient(135deg, #503830 0%, #44302a 100%)',
                '--bg-message-ai': '#302420',
                '--bg-message-announce': 'linear-gradient(135deg, #483028 0%, #302420 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #284030 0%, #20382a 100%)',
                '--bg-input': '#1e1410',
                '--bg-code': '#18120e',
                '--border-color': '#583828',
                '--border-message': '#604030',
                '--border-user': '#684838',
                '--text-primary': '#f0d8d0',
                '--text-secondary': '#c89888',
                '--text-muted': '#906058',
                '--text-code': '#e8c0b0',
                '--accent': '#c87868',
                '--accent-glow': 'rgba(200, 120, 104, 0.4)',
                '--error': '#f08080',
                '--error-bg': 'linear-gradient(135deg, #3a1a1a 0%, #2a0a0a 100%)',
                '--error-border': '#5a2a2a',
                '--important': '#dada80',
                '--important-bg': 'linear-gradient(135deg, #3a3a1a 0%, #2a2a0a 100%)',
                '--important-border': '#5a5a2a',
                '--info': '#80b0d0',
                '--info-bg': 'linear-gradient(135deg, #1a2a3a 0%, #0a1a2a 100%)',
                '--info-border': '#2a4a6a',
                '--button-bg': 'linear-gradient(135deg, #503830 0%, #403028 100%)',
                '--button-hover': 'linear-gradient(135deg, #604840 0%, #503830 100%)',
                '--button-stop': 'linear-gradient(135deg, #5a2a2a 0%, #3a1a1a 100%)',
                '--scrollbar': '#583828',
                '--scrollbar-hover': '#684838'
            }
        },
        'dark-catpuccin': {
            name: 'Catpuccin',
            mode: 'dark',
            vars: {
                '--bg-primary': '#1e1e2e',
                '--bg-secondary': '#181825',
                '--bg-tertiary': '#313244',
                '--bg-message-user': 'linear-gradient(135deg, #45475a 0%, #3b3b4f 100%)',
                '--bg-message-ai': '#313244',
                '--bg-message-announce': 'linear-gradient(135deg, #3a3b4a 0%, #313244 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #2e3a2e 0%, #243024 100%)',
                '--bg-input': '#1e1e2e',
                '--bg-code': '#11111b',
                '--border-color': '#45475a',
                '--border-message': '#585b70',
                '--border-user': '#6c6f85',
                '--text-primary': '#cdd6f4',
                '--text-secondary': '#bac2de',
                '--text-muted': '#6c7086',
                '--text-code': '#a6adc8',
                '--accent': '#cba6f7',
                '--accent-glow': 'rgba(203, 166, 247, 0.4)',
                '--error': '#f38ba8',
                '--error-bg': 'linear-gradient(135deg, #453038 0%, #352028 100%)',
                '--error-border': '#6c4050',
                '--important': '#f9e2af',
                '--important-bg': 'linear-gradient(135deg, #454030 0%, #353520 100%)',
                '--important-border': '#6c6050',
                '--info': '#89dceb',
                '--info-bg': 'linear-gradient(135deg, #283545 0%, #182535 100%)',
                '--info-border': '#405068',
                '--button-bg': 'linear-gradient(135deg, #45475a 0%, #35374a 100%)',
                '--button-hover': 'linear-gradient(135deg, #585b70 0%, #45475a 100%)',
                '--button-stop': 'linear-gradient(135deg, #5a2a2a 0%, #3a1a1a 100%)',
                '--scrollbar': '#45475a',
                '--scrollbar-hover': '#585b70'
            }
        },
        'dark-brown': {
            name: 'Brown',
            mode: 'dark',
            vars: {
                '--bg-primary': '#14100c',
                '--bg-secondary': '#201a14',
                '--bg-tertiary': '#2e2820',
                '--bg-message-user': 'linear-gradient(135deg, #483a28 0%, #3c3020 100%)',
                '--bg-message-ai': '#2e2820',
                '--bg-message-announce': 'linear-gradient(135deg, #403828 0%, #2e2820 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #304830 0%, #243824 100%)',
                '--bg-input': '#1a140e',
                '--bg-code': '#14100c',
                '--border-color': '#504028',
                '--border-message': '#584830',
                '--border-user': '#605038',
                '--text-primary': '#e8d8c8',
                '--text-secondary': '#b89870',
                '--text-muted': '#806850',
                '--text-code': '#d0c0a8',
                '--accent': '#a07840',
                '--accent-glow': 'rgba(160, 120, 64, 0.4)',
                '--error': '#f08080',
                '--error-bg': 'linear-gradient(135deg, #3a1a1a 0%, #2a0a0a 100%)',
                '--error-border': '#5a2a2a',
                '--important': '#dada80',
                '--important-bg': 'linear-gradient(135deg, #3a3a1a 0%, #2a2a0a 100%)',
                '--important-border': '#5a5a2a',
                '--info': '#80b0d0',
                '--info-bg': 'linear-gradient(135deg, #1a2a3a 0%, #0a1a2a 100%)',
                '--info-border': '#2a4a6a',
                '--button-bg': 'linear-gradient(135deg, #483a28 0%, #383020 100%)',
                '--button-hover': 'linear-gradient(135deg, #584a38 0%, #483a28 100%)',
                '--button-stop': 'linear-gradient(135deg, #5a2a2a 0%, #3a1a1a 100%)',
                '--scrollbar': '#504028',
                '--scrollbar-hover': '#605038'
            }
        },
        // Light themes
        'light-black': {
            name: 'Black',
            mode: 'light',
            vars: {
                '--bg-primary': '#ffffff',
                '--bg-secondary': '#f8f8f8',
                '--bg-tertiary': '#f0f0f0',
                '--bg-message-user': 'linear-gradient(135deg, #e8e8e8 0%, #e0e0e0 100%)',
                '--bg-message-ai': '#f5f5f5',
                '--bg-message-announce': 'linear-gradient(135deg, #f0f0f0 0%, #e8e8e8 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #e8f0e8 0%, #e0ebe0 100%)',
                '--bg-input': '#ffffff',
                '--bg-code': '#f8f8f8',
                '--border-color': '#d0d0d0',
                '--border-message': '#c8c8c8',
                '--border-user': '#b8b8b8',
                '--text-primary': '#1a1a1a',
                '--text-secondary': '#505050',
                '--text-muted': '#909090',
                '--text-code': '#303030',
                '--accent': '#000000',
                '--accent-glow': 'rgba(0, 0, 0, 0.2)',
                '--error': '#c04040',
                '--error-bg': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--error-border': '#d8a8a8',
                '--important': '#a08040',
                '--important-bg': 'linear-gradient(135deg, #f8f0d8 0%, #f0e8c8 100%)',
                '--important-border': '#d8c8a8',
                '--info': '#4080b0',
                '--info-bg': 'linear-gradient(135deg, #d8f0f8 0%, #c8e8f0 100%)',
                '--info-border': '#a8c8d8',
                '--button-bg': 'linear-gradient(135deg, #e8e8e8 0%, #d8d8d8 100%)',
                '--button-hover': 'linear-gradient(135deg, #d0d0d0 0%, #c0c0c0 100%)',
                '--button-stop': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--scrollbar': '#c0c0c0',
                '--scrollbar-hover': '#a0a0a0'
            }
        },
        'light-gray': {
            name: 'Gray',
            mode: 'light',
            vars: {
                '--bg-primary': '#f5f5f5',
                '--bg-secondary': '#e8e8e8',
                '--bg-tertiary': '#dcdcdc',
                '--bg-message-user': 'linear-gradient(135deg, #d8d8d8 0%, #d0d0d0 100%)',
                '--bg-message-ai': '#e0e0e0',
                '--bg-message-announce': 'linear-gradient(135deg, #d8d8d8 0%, #e8e8e8 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #d8e8d8 0%, #d0e0d0 100%)',
                '--bg-input': '#f0f0f0',
                '--bg-code': '#e8e8e8',
                '--border-color': '#b8b8b8',
                '--border-message': '#a8a8a8',
                '--border-user': '#989898',
                '--text-primary': '#202020',
                '--text-secondary': '#484848',
                '--text-muted': '#808080',
                '--text-code': '#383838',
                '--accent': '#6080a0',
                '--accent-glow': 'rgba(96, 128, 160, 0.3)',
                '--error': '#c04040',
                '--error-bg': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--error-border': '#d8a8a8',
                '--important': '#a08040',
                '--important-bg': 'linear-gradient(135deg, #f8f0d8 0%, #f0e8c8 100%)',
                '--important-border': '#d8c8a8',
                '--info': '#4080b0',
                '--info-bg': 'linear-gradient(135deg, #d8f0f8 0%, #c8e8f0 100%)',
                '--info-border': '#a8c8d8',
                '--button-bg': 'linear-gradient(135deg, #d8d8d8 0%, #c8c8c8 100%)',
                '--button-hover': 'linear-gradient(135deg, #c0c0c0 0%, #b0b0b0 100%)',
                '--button-stop': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--scrollbar': '#b0b0b0',
                '--scrollbar-hover': '#909090'
            }
        },
        'light-pink': {
            name: 'Pink',
            mode: 'light',
            vars: {
                '--bg-primary': '#fff8fa',
                '--bg-secondary': '#fff0f4',
                '--bg-tertiary': '#f8e8ec',
                '--bg-message-user': 'linear-gradient(135deg, #f8d8e4 0%, #f0d0dc 100%)',
                '--bg-message-ai': '#f8f0f4',
                '--bg-message-announce': 'linear-gradient(135deg, #f8e0e8 0%, #fff0f4 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #e0f0e0 0%, #d8ecd8 100%)',
                '--bg-input': '#fff8fa',
                '--bg-code': '#fff0f4',
                '--border-color': '#e8b8c8',
                '--border-message': '#d8a8b8',
                '--border-user': '#c898a8',
                '--text-primary': '#2a1820',
                '--text-secondary': '#684858',
                '--text-muted': '#a08090',
                '--text-code': '#483040',
                '--accent': '#d06090',
                '--accent-glow': 'rgba(208, 96, 144, 0.3)',
                '--error': '#c04040',
                '--error-bg': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--error-border': '#d8a8a8',
                '--important': '#a08040',
                '--important-bg': 'linear-gradient(135deg, #f8f0d8 0%, #f0e8c8 100%)',
                '--important-border': '#d8c8a8',
                '--info': '#4080b0',
                '--info-bg': 'linear-gradient(135deg, #d8f0f8 0%, #c8e8f0 100%)',
                '--info-border': '#a8c8d8',
                '--button-bg': 'linear-gradient(135deg, #f8d8e4 0%, #f0d0dc 100%)',
                '--button-hover': 'linear-gradient(135deg, #f0c8d8 0%, #e8c0d0 100%)',
                '--button-stop': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--scrollbar': '#e0b0c0',
                '--scrollbar-hover': '#c090a0'
            }
        },
        'light-magenta': {
            name: 'Magenta',
            mode: 'light',
            vars: {
                '--bg-primary': '#fff8fc',
                '--bg-secondary': '#fcf0f8',
                '--bg-tertiary': '#f8e8f4',
                '--bg-message-user': 'linear-gradient(135deg, #f8d8f0 0%, #f0d0e8 100%)',
                '--bg-message-ai': '#f8f0f8',
                '--bg-message-announce': 'linear-gradient(135deg, #f8e0f0 0%, #fcf0f8 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #e0f0e8 0%, #d8ecd8 100%)',
                '--bg-input': '#fff8fc',
                '--bg-code': '#fcf0f8',
                '--border-color': '#e8b0d8',
                '--border-message': '#d8a0c8',
                '--border-user': '#c890b8',
                '--text-primary': '#281828',
                '--text-secondary': '#684868',
                '--text-muted': '#a080a0',
                '--text-code': '#483048',
                '--accent': '#b060c8',
                '--accent-glow': 'rgba(176, 96, 200, 0.3)',
                '--error': '#c04040',
                '--error-bg': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--error-border': '#d8a8a8',
                '--important': '#a08040',
                '--important-bg': 'linear-gradient(135deg, #f8f0d8 0%, #f0e8c8 100%)',
                '--important-border': '#d8c8a8',
                '--info': '#4080b0',
                '--info-bg': 'linear-gradient(135deg, #d8f0f8 0%, #c8e8f0 100%)',
                '--info-border': '#a8c8d8',
                '--button-bg': 'linear-gradient(135deg, #f8d8f0 0%, #f0d0e8 100%)',
                '--button-hover': 'linear-gradient(135deg, #f0c8e8 0%, #e8c0e0 100%)',
                '--button-stop': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--scrollbar': '#e0a0d0',
                '--scrollbar-hover': '#c080b0'
            }
        },
        'light-violet': {
            name: 'Violet',
            mode: 'light',
            vars: {
                '--bg-primary': '#faf8ff',
                '--bg-secondary': '#f6f0fc',
                '--bg-tertiary': '#f0e8f8',
                '--bg-message-user': 'linear-gradient(135deg, #e8d8f8 0%, #e0d0f0 100%)',
                '--bg-message-ai': '#f4f0f8',
                '--bg-message-announce': 'linear-gradient(135deg, #f0e0f8 0%, #f6f0fc 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #e0f0e8 0%, #d8ecd8 100%)',
                '--bg-input': '#faf8ff',
                '--bg-code': '#f6f0fc',
                '--border-color': '#d0b8e8',
                '--border-message': '#c0a8d8',
                '--border-user': '#b098c8',
                '--text-primary': '#201830',
                '--text-secondary': '#484068',
                '--text-muted': '#8080a0',
                '--text-code': '#302850',
                '--accent': '#9060c0',
                '--accent-glow': 'rgba(144, 96, 192, 0.3)',
                '--error': '#c04040',
                '--error-bg': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--error-border': '#d8a8a8',
                '--important': '#a08040',
                '--important-bg': 'linear-gradient(135deg, #f8f0d8 0%, #f0e8c8 100%)',
                '--important-border': '#d8c8a8',
                '--info': '#4080b0',
                '--info-bg': 'linear-gradient(135deg, #d8f0f8 0%, #c8e8f0 100%)',
                '--info-border': '#a8c8d8',
                '--button-bg': 'linear-gradient(135deg, #e8d8f8 0%, #e0d0f0 100%)',
                '--button-hover': 'linear-gradient(135deg, #e0c8f0 0%, #d8c0e8 100%)',
                '--button-stop': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--scrollbar': '#c8b0e0',
                '--scrollbar-hover': '#a890c0'
            }
        },
        'light-purple': {
            name: 'Purple',
            mode: 'light',
            vars: {
                '--bg-primary': '#faf8fc',
                '--bg-secondary': '#f6f0f8',
                '--bg-tertiary': '#eee8f4',
                '--bg-message-user': 'linear-gradient(135deg, #e8d8f4 0%, #e0d0ec 100%)',
                '--bg-message-ai': '#f2f0f8',
                '--bg-message-announce': 'linear-gradient(135deg, #ede0f4 0%, #f6f0f8 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #e0f0e8 0%, #d8ecd8 100%)',
                '--bg-input': '#faf8fc',
                '--bg-code': '#f6f0f8',
                '--border-color': '#d0b0e0',
                '--border-message': '#c0a0d0',
                '--border-user': '#b090c0',
                '--text-primary': '#28182c',
                '--text-secondary': '#583868',
                '--text-muted': '#9078a0',
                '--text-code': '#382848',
                '--accent': '#a060c8',
                '--accent-glow': 'rgba(160, 96, 200, 0.3)',
                '--error': '#c04040',
                '--error-bg': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--error-border': '#d8a8a8',
                '--important': '#a08040',
                '--important-bg': 'linear-gradient(135deg, #f8f0d8 0%, #f0e8c8 100%)',
                '--important-border': '#d8c8a8',
                '--info': '#4080b0',
                '--info-bg': 'linear-gradient(135deg, #d8f0f8 0%, #c8e8f0 100%)',
                '--info-border': '#a8c8d8',
                '--button-bg': 'linear-gradient(135deg, #e8d8f4 0%, #e0d0ec 100%)',
                '--button-hover': 'linear-gradient(135deg, #e0c8f0 0%, #d8c0e8 100%)',
                '--button-stop': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--scrollbar': '#c8a8d8',
                '--scrollbar-hover': '#a888b8'
            }
        },
        'light-blue': {
            name: 'Blue',
            mode: 'light',
            vars: {
                '--bg-primary': '#f8faff',
                '--bg-secondary': '#f0f4fc',
                '--bg-tertiary': '#e8ecf8',
                '--bg-message-user': 'linear-gradient(135deg, #d8e4f8 0%, #d0dcf0 100%)',
                '--bg-message-ai': '#f0f4fc',
                '--bg-message-announce': 'linear-gradient(135deg, #e0e8f8 0%, #f0f4fc 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #e0f0e8 0%, #d8ecd8 100%)',
                '--bg-input': '#f8faff',
                '--bg-code': '#f0f4fc',
                '--border-color': '#b8c8e8',
                '--border-message': '#a8b8d8',
                '--border-user': '#98a8c8',
                '--text-primary': '#182030',
                '--text-secondary': '#384868',
                '--text-muted': '#7888a8',
                '--text-code': '#283858',
                '--accent': '#4080c0',
                '--accent-glow': 'rgba(64, 128, 192, 0.3)',
                '--error': '#c04040',
                '--error-bg': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--error-border': '#d8a8a8',
                '--important': '#a08040',
                '--important-bg': 'linear-gradient(135deg, #f8f0d8 0%, #f0e8c8 100%)',
                '--important-border': '#d8c8a8',
                '--info': '#4080b0',
                '--info-bg': 'linear-gradient(135deg, #d8f0f8 0%, #c8e8f0 100%)',
                '--info-border': '#a8c8d8',
                '--button-bg': 'linear-gradient(135deg, #d8e4f8 0%, #d0dcf0 100%)',
                '--button-hover': 'linear-gradient(135deg, #c8d8f0 0%, #c0d0e8 100%)',
                '--button-stop': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--scrollbar': '#b0c0e0',
                '--scrollbar-hover': '#90a0c0'
            }
        },
        'light-green': {
            name: 'Green',
            mode: 'light',
            vars: {
                '--bg-primary': '#f8fff8',
                '--bg-secondary': '#f0fcf0',
                '--bg-tertiary': '#e8f8e8',
                '--bg-message-user': 'linear-gradient(135deg, #d8f0d8 0%, #d0ecd0 100%)',
                '--bg-message-ai': '#f0fcf0',
                '--bg-message-announce': 'linear-gradient(135deg, #e0f8e0 0%, #f0fcf0 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #e8f0d8 0%, #e0ecd0 100%)',
                '--bg-input': '#f8fff8',
                '--bg-code': '#f0fcf0',
                '--border-color': '#a8d0a8',
                '--border-message': '#98c098',
                '--border-user': '#88b088',
                '--text-primary': '#182818',
                '--text-secondary': '#386838',
                '--text-muted': '#709870',
                '--text-code': '#285828',
                '--accent': '#40a060',
                '--accent-glow': 'rgba(64, 160, 96, 0.3)',
                '--error': '#c04040',
                '--error-bg': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--error-border': '#d8a8a8',
                '--important': '#a08040',
                '--important-bg': 'linear-gradient(135deg, #f8f0d8 0%, #f0e8c8 100%)',
                '--important-border': '#d8c8a8',
                '--info': '#4080b0',
                '--info-bg': 'linear-gradient(135deg, #d8f0f8 0%, #c8e8f0 100%)',
                '--info-border': '#a8c8d8',
                '--button-bg': 'linear-gradient(135deg, #d8f0d8 0%, #d0ecd0 100%)',
                '--button-hover': 'linear-gradient(135deg, #c8e8c8 0%, #c0e0c0 100%)',
                '--button-stop': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--scrollbar': '#a0d0a0',
                '--scrollbar-hover': '#80b080'
            }
        },
        'light-red': {
            name: 'Red',
            mode: 'light',
            vars: {
                '--bg-primary': '#fffcfc',
                '--bg-secondary': '#fcf4f4',
                '--bg-tertiary': '#f8ecec',
                '--bg-message-user': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--bg-message-ai': '#fcf4f4',
                '--bg-message-announce': 'linear-gradient(135deg, #f8e0e0 0%, #fcf4f4 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #e0f0e0 0%, #d8ecd8 100%)',
                '--bg-input': '#fffcfc',
                '--bg-code': '#fcf4f4',
                '--border-color': '#d8b0b0',
                '--border-message': '#c8a0a0',
                '--border-user': '#b89090',
                '--text-primary': '#281818',
                '--text-secondary': '#683838',
                '--text-muted': '#a08080',
                '--text-code': '#482828',
                '--accent': '#c04040',
                '--accent-glow': 'rgba(192, 64, 64, 0.3)',
                '--error': '#c04040',
                '--error-bg': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--error-border': '#d8a8a8',
                '--important': '#a08040',
                '--important-bg': 'linear-gradient(135deg, #f8f0d8 0%, #f0e8c8 100%)',
                '--important-border': '#d8c8a8',
                '--info': '#4080b0',
                '--info-bg': 'linear-gradient(135deg, #d8f0f8 0%, #c8e8f0 100%)',
                '--info-border': '#a8c8d8',
                '--button-bg': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--button-hover': 'linear-gradient(135deg, #e8c8c8 0%, #e0c0c0 100%)',
                '--button-stop': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--scrollbar': '#d0a0a0',
                '--scrollbar-hover': '#b08080'
            }
        },
        'light-sepia': {
            name: 'Sepia',
            mode: 'light',
            vars: {
                '--bg-primary': '#faf8f4',
                '--bg-secondary': '#f6f0e8',
                '--bg-tertiary': '#f0e8dc',
                '--bg-message-user': 'linear-gradient(135deg, #f0e0d0 0%, #e8d8c8 100%)',
                '--bg-message-ai': '#f6f0e8',
                '--bg-message-announce': 'linear-gradient(135deg, #f0e4d8 0%, #f6f0e8 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #e0f0e0 0%, #d8ecd8 100%)',
                '--bg-input': '#faf8f4',
                '--bg-code': '#f6f0e8',
                '--border-color': '#d8c8a8',
                '--border-message': '#c8b898',
                '--border-user': '#b8a888',
                '--text-primary': '#2a2018',
                '--text-secondary': '#684828',
                '--text-muted': '#a08060',
                '--text-code': '#483018',
                '--accent': '#a08040',
                '--accent-glow': 'rgba(160, 128, 64, 0.3)',
                '--error': '#c04040',
                '--error-bg': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--error-border': '#d8a8a8',
                '--important': '#a08040',
                '--important-bg': 'linear-gradient(135deg, #f8f0d8 0%, #f0e8c8 100%)',
                '--important-border': '#d8c8a8',
                '--info': '#4080b0',
                '--info-bg': 'linear-gradient(135deg, #d8f0f8 0%, #c8e8f0 100%)',
                '--info-border': '#a8c8d8',
                '--button-bg': 'linear-gradient(135deg, #f0e0d0 0%, #e8d8c8 100%)',
                '--button-hover': 'linear-gradient(135deg, #e8d8c0 0%, #e0d0b8 100%)',
                '--button-stop': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--scrollbar': '#d0c0a0',
                '--scrollbar-hover': '#b0a080'
            }
        },
        'light-silver': {
            name: 'Silver',
            mode: 'light',
            vars: {
                '--bg-primary': '#fafafa',
                '--bg-secondary': '#f4f4f4',
                '--bg-tertiary': '#ececec',
                '--bg-message-user': 'linear-gradient(135deg, #e4e4e4 0%, #dcdcdc 100%)',
                '--bg-message-ai': '#f0f0f0',
                '--bg-message-announce': 'linear-gradient(135deg, #e8e8e8 0%, #f4f4f4 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #e0e8e0 0%, #d8ecd8 100%)',
                '--bg-input': '#fafafa',
                '--bg-code': '#f4f4f4',
                '--border-color': '#c8c8c8',
                '--border-message': '#b8b8b8',
                '--border-user': '#a8a8a8',
                '--text-primary': '#202020',
                '--text-secondary': '#505050',
                '--text-muted': '#808080',
                '--text-code': '#303030',
                '--accent': '#7088a0',
                '--accent-glow': 'rgba(112, 136, 160, 0.3)',
                '--error': '#c04040',
                '--error-bg': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--error-border': '#d8a8a8',
                '--important': '#a08040',
                '--important-bg': 'linear-gradient(135deg, #f8f0d8 0%, #f0e8c8 100%)',
                '--important-border': '#d8c8a8',
                '--info': '#4080b0',
                '--info-bg': 'linear-gradient(135deg, #d8f0f8 0%, #c8e8f0 100%)',
                '--info-border': '#a8c8d8',
                '--button-bg': 'linear-gradient(135deg, #e4e4e4 0%, #dcdcdc 100%)',
                '--button-hover': 'linear-gradient(135deg, #d4d4d4 0%, #cccccc 100%)',
                '--button-stop': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--scrollbar': '#c0c0c0',
                '--scrollbar-hover': '#a0a0a0'
            }
        },
        'light-gold': {
            name: 'Gold',
            mode: 'light',
            vars: {
                '--bg-primary': '#fffcf4',
                '--bg-secondary': '#fcf8ec',
                '--bg-tertiary': '#f8f0d8',
                '--bg-message-user': 'linear-gradient(135deg, #f8e8c8 0%, #f0e0b8 100%)',
                '--bg-message-ai': '#fcf8ec',
                '--bg-message-announce': 'linear-gradient(135deg, #f8ecc0 0%, #fcf8ec 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #e0f0e0 0%, #d8ecd8 100%)',
                '--bg-input': '#fffcf4',
                '--bg-code': '#fcf8ec',
                '--border-color': '#d8c088',
                '--border-message': '#c8b078',
                '--border-user': '#b8a068',
                '--text-primary': '#2a2010',
                '--text-secondary': '#684820',
                '--text-muted': '#a08050',
                '--text-code': '#483010',
                '--accent': '#b09040',
                '--accent-glow': 'rgba(176, 144, 64, 0.3)',
                '--error': '#c04040',
                '--error-bg': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--error-border': '#d8a8a8',
                '--important': '#a08040',
                '--important-bg': 'linear-gradient(135deg, #f8f0d8 0%, #f0e8c8 100%)',
                '--important-border': '#d8c8a8',
                '--info': '#4080b0',
                '--info-bg': 'linear-gradient(135deg, #d8f0f8 0%, #c8e8f0 100%)',
                '--info-border': '#a8c8d8',
                '--button-bg': 'linear-gradient(135deg, #f8e8c8 0%, #f0e0b8 100%)',
                '--button-hover': 'linear-gradient(135deg, #f0e0b8 0%, #e8d8a8 100%)',
                '--button-stop': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--scrollbar': '#d0c088',
                '--scrollbar-hover': '#b0a068'
            }
        },
        'light-rosegold': {
            name: 'Rose Gold',
            mode: 'light',
            vars: {
                '--bg-primary': '#fffcfa',
                '--bg-secondary': '#fcf4f0',
                '--bg-tertiary': '#f8ece4',
                '--bg-message-user': 'linear-gradient(135deg, #f8e4d8 0%, #f0d8c8 100%)',
                '--bg-message-ai': '#fcf4f0',
                '--bg-message-announce': 'linear-gradient(135deg, #f8e4dc 0%, #fcf4f0 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #e0f0e0 0%, #d8ecd8 100%)',
                '--bg-input': '#fffcfa',
                '--bg-code': '#fcf4f0',
                '--border-color': '#d8b8a8',
                '--border-message': '#c8a898',
                '--border-user': '#b89888',
                '--text-primary': '#2a1818',
                '--text-secondary': '#684038',
                '--text-muted': '#a08078',
                '--text-code': '#483028',
                '--accent': '#b87868',
                '--accent-glow': 'rgba(184, 120, 104, 0.3)',
                '--error': '#c04040',
                '--error-bg': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--error-border': '#d8a8a8',
                '--important': '#a08040',
                '--important-bg': 'linear-gradient(135deg, #f8f0d8 0%, #f0e8c8 100%)',
                '--important-border': '#d8c8a8',
                '--info': '#4080b0',
                '--info-bg': 'linear-gradient(135deg, #d8f0f8 0%, #c8e8f0 100%)',
                '--info-border': '#a8c8d8',
                '--button-bg': 'linear-gradient(135deg, #f8e4d8 0%, #f0d8c8 100%)',
                '--button-hover': 'linear-gradient(135deg, #f0dcc8 0%, #e8d4b8 100%)',
                '--button-stop': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--scrollbar': '#d0b0a0',
                '--scrollbar-hover': '#b09080'
            }
        },
        'light-catpuccin': {
            name: 'Catpuccin',
            mode: 'light',
            vars: {
                '--bg-primary': '#eff1f5',
                '--bg-secondary': '#e6e9ef',
                '--bg-tertiary': '#dce0e8',
                '--bg-message-user': 'linear-gradient(135deg, #ccd0da 0%, #bcc0cc 100%)',
                '--bg-message-ai': '#e6e9ef',
                '--bg-message-announce': 'linear-gradient(135deg, #d0d4de 0%, #e6e9ef 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #d0e6d0 0%, #c8dcc8 100%)',
                '--bg-input': '#eff1f5',
                '--bg-code': '#e6e9ef',
                '--border-color': '#bcc0cc',
                '--border-message': '#acb0bc',
                '--border-user': '#9ca0ac',
                '--text-primary': '#4c4f69',
                '--text-secondary': '#5c5f72',
                '--text-muted': '#8c8fa1',
                '--text-code': '#5c5f72',
                '--accent': '#8839ef',
                '--accent-glow': 'rgba(136, 57, 239, 0.3)',
                '--error': '#d20f39',
                '--error-bg': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--error-border': '#d8a8a8',
                '--important': '#df8e1d',
                '--important-bg': 'linear-gradient(135deg, #f8f0d8 0%, #f0e8c8 100%)',
                '--important-border': '#d8c8a8',
                '--info': '#179299',
                '--info-bg': 'linear-gradient(135deg, #d8f0f8 0%, #c8e8f0 100%)',
                '--info-border': '#a8c8d8',
                '--button-bg': 'linear-gradient(135deg, #ccd0da 0%, #bcc0cc 100%)',
                '--button-hover': 'linear-gradient(135deg, #bcc0cc 0%, #acb0bc 100%)',
                '--button-stop': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--scrollbar': '#bcc0cc',
                '--scrollbar-hover': '#acb0bc'
            }
        },
        'light-brown': {
            name: 'Brown',
            mode: 'light',
            vars: {
                '--bg-primary': '#faf8f4',
                '--bg-secondary': '#f4f0e8',
                '--bg-tertiary': '#e8e0d4',
                '--bg-message-user': 'linear-gradient(135deg, #e8d8c0 0%, #e0d0b8 100%)',
                '--bg-message-ai': '#f4f0e8',
                '--bg-message-announce': 'linear-gradient(135deg, #e8e0d0 0%, #f4f0e8 100%)',
                '--bg-message-command': 'linear-gradient(135deg, #e0f0e0 0%, #d8ecd8 100%)',
                '--bg-input': '#faf8f4',
                '--bg-code': '#f4f0e8',
                '--border-color': '#c8b898',
                '--border-message': '#b8a888',
                '--border-user': '#a89878',
                '--text-primary': '#2a2018',
                '--text-secondary': '#584828',
                '--text-muted': '#907850',
                '--text-code': '#483818',
                '--accent': '#a07840',
                '--accent-glow': 'rgba(160, 120, 64, 0.3)',
                '--error': '#c04040',
                '--error-bg': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--error-border': '#d8a8a8',
                '--important': '#a08040',
                '--important-bg': 'linear-gradient(135deg, #f8f0d8 0%, #f0e8c8 100%)',
                '--important-border': '#d8c8a8',
                '--info': '#4080b0',
                '--info-bg': 'linear-gradient(135deg, #d8f0f8 0%, #c8e8f0 100%)',
                '--info-border': '#a8c8d8',
                '--button-bg': 'linear-gradient(135deg, #e8d8c0 0%, #e0d0b8 100%)',
                '--button-hover': 'linear-gradient(135deg, #e0d0b8 0%, #d8c8a8 100%)',
                '--button-stop': 'linear-gradient(135deg, #f8d8d8 0%, #f0d0d0 100%)',
                '--scrollbar': '#c8b090',
                '--scrollbar-hover': '#a89070'
            }
        }
    };

        let currentTheme = 'dark-black';

        function applyTheme(themeId) {
            const theme = themes[themeId];
            if (!theme) return;

            const root = document.documentElement;
            for (const [varName, value] of Object.entries(theme.vars)) {
                root.style.setProperty(varName, value);
            }

            currentTheme = themeId;
            localStorage.setItem('theme', themeId);
            updateThemeButtons();
        }

        function updateThemeButtons() {
            document.querySelectorAll('.theme-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.theme === currentTheme);
            });
        }

        function createThemeButtons() {
            const grid = document.getElementById('theme-grid');
            grid.innerHTML = '';

            // Group by mode
            const darkThemes = Object.entries(themes).filter(([id, t]) => t.mode === 'dark');
            const lightThemes = Object.entries(themes).filter(([id, t]) => t.mode === 'light');

            const createButtons = (themeList) => {
                themeList.forEach(([id, theme]) => {
                    const btn = document.createElement('button');
                    btn.className = 'theme-btn' + (id === currentTheme ? ' active' : '');
                    btn.dataset.theme = id;

                    // Get preview colors from theme
                    const bgColor = theme.vars['--bg-primary'];
                    const accentColor = theme.vars['--accent'];
                    const textColor = theme.vars['--text-primary'];

                    btn.innerHTML = `
                        <div class="theme-preview" style="background: linear-gradient(135deg, ${bgColor} 50%, ${accentColor} 50%);"></div>
                        ${theme.name}
                    `;

                    btn.onclick = () => applyTheme(id);
                    grid.appendChild(btn);
                });
            };

            createButtons(darkThemes);
            createButtons(lightThemes);
        }

        function toggleSettings() {
            const overlay = document.getElementById('settings-overlay');
            const modal = document.getElementById('settings-modal');

            overlay.classList.toggle('show');
            modal.classList.toggle('show');
        }

        function closeSettings(event) {
            if (event.target.id === 'settings-overlay') {
                toggleSettings();
            }
        }

        // Load saved theme on page load
        function loadTheme() {
            const saved = localStorage.getItem('theme');
            if (saved && themes[saved]) {
                applyTheme(saved);
            } else {
                applyTheme('dark-black');
            }
            createThemeButtons();
        }

    </script>
    <script>
        // Register Service Worker for PWA
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js')
                    .then(reg => console.log('Service Worker registered'))
                    .catch(err => console.log('Service Worker registration failed:', err));
            });
        }

        updateConnectionStatus('connecting');

        // Check connection immediately and start monitoring
        setTimeout(() => {
            checkConnection().catch(err => {
                // If initial check fails, start reconnecting
                isConnected = false;
                updateConnectionStatus('disconnected');
                addAnnouncement('Disconnected from server. Reconnecting...', false, false, true);
                scheduleReconnect();
            });
        }, 100);

        // Start polling for announcements
        setInterval(() => {
            if (isConnected) pollAnnouncements();
        }, 500);

        loadHistory();

        // Call loadTheme at startup
        loadTheme();
    </script>
</body>
</html>
'''

class Webui(core.channel.Channel):
    """
    A web-based channel for communicating with the AI through a browser interface.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.announcement_queue = []
        self.announcement_id = 0
        self.main_loop = None

    async def on_ready(self):
        asyncio.sleep(2)
        await self.announce("Server is up!")

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
        port = core.config.get("webui_port", 5000)
        core.log("webui", f"WebUI started on {host}:{port}")

        while True:
            await asyncio.sleep(1)

    def _run_flask(self):
        """Run Flask in a separate thread."""
        import socket
        from werkzeug.serving import make_server

        host = core.config.get("webui_host", "127.0.0.1")
        port = core.config.get("webui_port", 5000)

        server = make_server(host, port, app, threaded=True)
        server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.serve_forever()

    async def announce(self, message: str, type: str = None):
        """
        Handle announcements from the framework and push to web UI.
        """
        core.log("webui channel", f"Announcement: {message}")
        self.announcement_id += 1
        self.announcement_queue.append({
            'id': self.announcement_id,
            'content': message.replace('\n', '<br>'),
            'type': type,
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

# Add at the top with other globals
stream_cancellations = set()

@app.route('/stream', methods=['POST'])
def stream_message():
    """Stream AI response token by token."""
    global channel_instance
    data = request.get_json()
    user_message = data.get('message', '')
    import uuid
    stream_id = str(uuid.uuid4())[:8]

    def generate():
        from queue import Queue
        token_queue = Queue()
        done = object()

        async def collect_tokens():
            try:
                async for token in channel_instance.send_stream("user", user_message):
                    if stream_id in stream_cancellations:
                        stream_cancellations.discard(stream_id)
                        token_queue.put(('cancelled', True))
                        break
                    token_queue.put(token)
            except Exception as e:
                token_queue.put(('error', str(e)))
            finally:
                token_queue.put(done)

        future = asyncio.run_coroutine_threadsafe(collect_tokens(), channel_instance.main_loop)

        yield f"data: {json.dumps({'id': stream_id})}\n\n"

        while True:
            item = token_queue.get()
            if item is done:
                yield f"data: {json.dumps({'done': True})}\n\n"
                break
            elif isinstance(item, tuple):
                if item[0] == 'error':
                    yield f"data: {json.dumps({'error': item[1]})}\n\n"
                    break
                elif item[0] == 'cancelled':
                    yield f"data: {json.dumps({'cancelled': True})}\n\n"
                    break
            else:
                yield f"data: {json.dumps({'token': item})}\n\n"

        future.result()

    return Response(generate(), mimetype='text/event-stream')

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

@app.route('/cancel', methods=['POST'])
def cancel_stream():
    """Cancel an ongoing stream"""
    global channel_instance

    data = request.get_json()
    stream_id = data.get('id')

    # Set the cancel flag on the API
    if channel_instance:
        channel_instance.manager.API.cancel_request = True

    if stream_id:
        stream_cancellations.add(stream_id)

    return jsonify({'success': True})

@app.route('/upload', methods=['POST'])
def upload_file():
    global channel_instance
    data = request.get_json()
    filename = data.get('filename', '')
    content_b64 = data.get('content', '')
    mimetype = data.get('mimetype', '')

    try:
        import base64
        content = base64.b64decode(content_b64).decode('utf-8', errors='replace')

        # You can customize what to do with the file content here
        # For example, send it to the AI as context
        result = f"File uploaded: {filename} ({len(content)} bytes)"

        channel_instance.manager.API.insert_turn("user", f"[File: {filename}]\n{content[:1000]}...")
        # Or process it through the channel
        # future = asyncio.run_coroutine_threadsafe(
        #     channel_instance.send("user", f"[File: {filename}]\n{content[:1000]}..."),
        #     channel_instance.main_loop
        # )
        # response = future.result()

        return jsonify({'success': True, 'message': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# == PWA Support ==
@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "OptiClaw",
        "short_name": "OptiClaw",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#111111",
        "theme_color": "#111111",
        "orientation": "portrait-primary",
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}
        ]
    })

@app.route('/sw.js')
def service_worker():
    return '''
const CACHE_NAME = 'ai-chat-v1';
const urlsToCache = ['/', '/manifest.json'];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request);
        })
    );
});
''', 200, {'Content-Type': 'application/javascript'}

@app.route('/icon-192.png')
@app.route('/icon-512.png')
def icon():
    # Generate a simple SVG icon and return it as PNG would require a library.
    # Here we return a minimal valid placeholder (or you can serve a real file).
    # A 1x1 transparent pixel PNG:
    import base64
    # Transparent pixel
    # png_data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==')
    # Simple colored square (black) - 192x192
    # Using a minimal valid PNG generator is complex inline, so using a simple SVG approach for icons:
    # For PWA to work, you need actual files or inline data URIs.
    # This creates a simple black PNG placeholder.
    # Better to create actual files, but for a single-file solution:
    # We'll just serve the same placeholder for both.

    # Minimal black PNG (2x2)
    png_hex = "89504e470d0a1a0a0000000d494844520000000200000002080200000001f338dd0000000c4944415408d763f8ffffcf0001000100737a55b00000000049454e44ae426082"
    return bytes.fromhex(png_hex), 200, {'Content-Type': 'image/png'}
