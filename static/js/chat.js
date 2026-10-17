function getAvatarSrc(avatar) {
    if (!avatar) return '/static/images/avatars/human_male.svg';
    if (avatar.startsWith('/') || avatar.startsWith('http://') || avatar.startsWith('https://')) {
        return avatar;
    }
    return `/static/images/avatars/${avatar}.svg`;
}

class TavernChatManager {
    constructor() {
        this.lastMessageId = 0;
        this.chatWs = null;
        this.whisperWs = null;
        this.pollInterval = null;
        this.whisperPollInterval = null;
        this.isScrolledToBottom = true;
        this.activeWhisperFriendId = null;
        this.activeWhispers = {}; // friendId -> { friendInfo, messages: [], lastId: 0, unread: 0 }
        this.emojis = ['⚔️', '🛡️', '🦁', '🐺', '👑', '💀', '🍖', '💰', '🔥', '🧙', '🏹', '🗡️', '📜', '🎮', '❤️', '🏆', '✨', '⚡', '🌍', '💎'];
    }

    init() {
        this.setupEventListeners();
        this.initChatWebSocket();
        this.initWhisperWebSocket();
        this.loadInitialMessages();
        this.loadWhisperConversations();

        // Polling fallback every 2.5s in case websocket disconnects
        this.pollInterval = setInterval(() => {
            if (!this.chatWs || this.chatWs.readyState !== WebSocket.OPEN) {
                this.pollMessages();
            }
        }, 2500);

        // Whisper poll fallback
        this.whisperPollInterval = setInterval(() => {
            if (window.currentUser) {
                this.pollWhispers();
            }
        }, 3000);
    }

    initChatWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat`;

        try {
            this.chatWs = new WebSocket(wsUrl);
            this.chatWs.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'chat_message' && data.message) {
                        this.appendMessage(data.message, true);
                    }
                } catch(e) {
                    console.error('WS Parse error', e);
                }
            };
            this.chatWs.onclose = () => {
                setTimeout(() => this.initChatWebSocket(), 4000);
            };
        } catch(e) {
            console.log('WS not supported, relying on polling');
        }
    }

    initWhisperWebSocket() {
        if (!window.currentUser) return;
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/whispers`;

        try {
            this.whisperWs = new WebSocket(wsUrl);
            this.whisperWs.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'whisper_message' && data.message) {
                        this.handleIncomingWhisper(data.message);
                    }
                } catch(e) {
                    console.error('Whisper WS Parse error', e);
                }
            };
            this.whisperWs.onclose = () => {
                if (window.currentUser) {
                    setTimeout(() => this.initWhisperWebSocket(), 4000);
                }
            };
        } catch(e) {}
    }

    setupEventListeners() {
        const chatInput = document.getElementById('chat-input-text');
        const sendBtn = document.getElementById('chat-send-btn');
        const emojiBtn = document.getElementById('chat-emoji-btn');
        const emojiPicker = document.getElementById('chat-emoji-picker');
        const messagesContainer = document.getElementById('chat-messages-box');

        if (chatInput) {
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }

        if (emojiBtn && emojiPicker) {
            // Populate emoji picker
            emojiPicker.innerHTML = this.emojis.map(e => `<span class="emoji-item" data-emoji="${e}">${e}</span>`).join('');
            emojiBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                emojiPicker.classList.toggle('hidden');
            });

            emojiPicker.addEventListener('click', (e) => {
                const target = e.target.closest('.emoji-item');
                if (target) {
                    const emoji = target.getAttribute('data-emoji');
                    if (chatInput) {
                        chatInput.value += emoji + ' ';
                        chatInput.focus();
                    }
                    emojiPicker.classList.add('hidden');
                }
            });

            document.addEventListener('click', (e) => {
                if (!emojiPicker.contains(e.target) && e.target !== emojiBtn) {
                    emojiPicker.classList.add('hidden');
                }
            });
        }

        if (messagesContainer) {
            messagesContainer.addEventListener('scroll', () => {
                const threshold = 60;
                this.isScrolledToBottom = messagesContainer.scrollHeight - messagesContainer.scrollTop - messagesContainer.clientHeight < threshold;
                const scrollBtn = document.getElementById('chat-scroll-bottom-btn');
                if (scrollBtn) {
                    scrollBtn.style.display = this.isScrolledToBottom ? 'none' : 'block';
                }
            });
        }

        const scrollBtn = document.getElementById('chat-scroll-bottom-btn');
        if (scrollBtn) {
            scrollBtn.addEventListener('click', () => {
                this.scrollToBottom();
            });
        }
    }

    async loadInitialMessages() {
        try {
            const res = await fetch('/api/chat/messages');
            const messages = await res.json();
            const container = document.getElementById('chat-messages-box');
            if (container) {
                container.innerHTML = '';
                messages.forEach(msg => {
                    this.appendMessage(msg, false);
                });
                this.scrollToBottom();
            }
        } catch(e) {
            console.error('Failed to load chat messages', e);
        }
    }

    async pollMessages() {
        try {
            const res = await fetch(`/api/chat/messages?last_id=${this.lastMessageId}`);
            const messages = await res.json();
            if (Array.isArray(messages) && messages.length > 0) {
                messages.forEach(msg => {
                    this.appendMessage(msg, true);
                });
            }
        } catch(e){}
    }

    async sendMessage() {
        if (!window.currentUser) {
            window.showAuthModal('login');
            return;
        }

        const input = document.getElementById('chat-input-text');
        if (!input) return;
        const text = input.value.trim();
        if (!text) return;

        try {
            const res = await fetch('/api/chat/messages', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            const data = await res.json();
            if (data.success) {
                input.value = '';
                if (window.tavernAudio) window.tavernAudio.playClick();
                // If WS wasn't connected, append directly
                if (!this.chatWs || this.chatWs.readyState !== WebSocket.OPEN) {
                    this.appendMessage(data.message, true);
                }
            } else if (data.error) {
                alert(data.error);
            }
        } catch(e) {
            console.error('Send error', e);
        }
    }

    appendMessage(msg, isNew = false) {
        if (msg.id <= this.lastMessageId) return;
        this.lastMessageId = msg.id;

        const container = document.getElementById('chat-messages-box');
        if (!container) return;

        const isMe = window.currentUser && window.currentUser.id === msg.user_id;
        const faction = msg.faction || 'none';
        const wowClass = msg.wow_class || 'warrior';
        const avatar = msg.avatar || 'human_male';

        // Parse time format
        let timeStr = '';
        if (msg.created_at) {
            const d = new Date(msg.created_at);
            timeStr = `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
        }

        // Format markdown-like bold and links safely
        let formattedText = this.escapeHtml(msg.text);
        formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        const el = document.createElement('div');
        el.className = `chat-message-row faction-border-${faction} ${isMe ? 'my-message' : ''}`;
        el.innerHTML = `
            <div class="chat-msg-avatar" onclick="tavernChat.openWhisper(${msg.user_id}, '${this.escapeJs(msg.character_name)}')">
                <img src="${getAvatarSrc(avatar)}" alt="${avatar}" />
                <span class="chat-faction-badge faction-badge-${faction}"></span>
            </div>
            <div class="chat-msg-body">
                <div class="chat-msg-header">
                    <span class="chat-author class-color-${wowClass}" 
                          onclick="tavernChat.openWhisper(${msg.user_id}, '${this.escapeJs(msg.character_name)}')"
                          title="Нажмите, чтобы шепнуть в ПМ">
                        ${this.escapeHtml(msg.character_name)}
                    </span>
                    <span class="chat-class-badge" title="${wowClass}">
                        <img src="/static/images/classes/${wowClass}.svg" alt="${wowClass}" />
                    </span>
                    <span class="chat-timestamp">${timeStr}</span>
                </div>
                <div class="chat-msg-content">${formattedText}</div>
            </div>
        `;

        container.appendChild(el);

        if (isNew) {
            if (window.tavernAudio && !isMe) {
                window.tavernAudio.playClick();
            }
            if (this.isScrolledToBottom || isMe) {
                this.scrollToBottom();
            }
        }
    }

    scrollToBottom() {
        const container = document.getElementById('chat-messages-box');
        if (container) {
            container.scrollTop = container.scrollHeight;
            this.isScrolledToBottom = true;
            const scrollBtn = document.getElementById('chat-scroll-bottom-btn');
            if (scrollBtn) scrollBtn.style.display = 'none';
        }
    }

    // --- WHISPER DOCK SYSTEM ---

    async loadWhisperConversations() {
        if (!window.currentUser) return;
        try {
            const res = await fetch('/api/whispers/conversations');
            const convos = await res.json();
            if (Array.isArray(convos)) {
                let totalUnread = 0;
                convos.forEach(c => {
                    totalUnread += c.unread_count;
                });
                this.updateGlobalWhisperBadge(totalUnread);
            }
        } catch(e){}
    }

    async pollWhispers() {
        if (!this.activeWhisperFriendId) return;
        const friendId = this.activeWhisperFriendId;
        const currentData = this.activeWhispers[friendId];
        const lastId = currentData ? currentData.lastId : 0;

        try {
            const res = await fetch(`/api/whispers/${friendId}?last_id=${lastId}`);
            const data = await res.json();
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(m => this.appendWhisperMessage(friendId, m));
            }
        } catch(e){}
    }

    async openWhisper(friendId, friendName) {
        if (!window.currentUser) {
            window.showAuthModal('login');
            return;
        }
        if (window.currentUser.id === friendId) {
            return; // Can't whisper oneself
        }

        this.activeWhisperFriendId = friendId;
        const dock = document.getElementById('whisper-dock');
        if (dock) dock.classList.remove('hidden');

        if (!this.activeWhispers[friendId]) {
            this.activeWhispers[friendId] = {
                name: friendName,
                lastId: 0,
                messages: []
            };
        }

        this.renderWhisperTabs();
        await this.loadWhisperHistory(friendId);
        
        const input = document.getElementById('whisper-input-text');
        if (input) {
            input.placeholder = `Шепнуть [${friendName}]...`;
            input.focus();
        }

        if (window.tavernAudio) window.tavernAudio.playClick();
    }

    async loadWhisperHistory(friendId) {
        try {
            const res = await fetch(`/api/whispers/${friendId}`);
            const data = await res.json();
            if (data.friend) {
                this.activeWhispers[friendId].friendInfo = data.friend;
                this.activeWhispers[friendId].name = data.friend.character_name;
            }

            const box = document.getElementById('whisper-messages-box');
            if (box) {
                box.innerHTML = '';
                if (data.messages && data.messages.length > 0) {
                    data.messages.forEach(m => this.appendWhisperMessage(friendId, m));
                } else {
                    box.innerHTML = `<div class="whisper-empty-hint">Начало переписки с <strong>${this.escapeHtml(this.activeWhispers[friendId].name)}</strong>. Поприветствуйте друга! 🍻</div>`;
                }
                box.scrollTop = box.scrollHeight;
            }
            this.renderWhisperTabs();
        } catch(e){
            console.error(e);
        }
    }

    appendWhisperMessage(friendId, msg) {
        if (!this.activeWhispers[friendId]) return;
        if (msg.id <= this.activeWhispers[friendId].lastId) return;
        this.activeWhispers[friendId].lastId = msg.id;

        if (this.activeWhisperFriendId === friendId) {
            const box = document.getElementById('whisper-messages-box');
            if (!box) return;

            const isMe = msg.sender_id === window.currentUser.id;
            const timeStr = msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : '';

            const row = document.createElement('div');
            row.className = `whisper-row ${isMe ? 'whisper-outgoing' : 'whisper-incoming'}`;
            row.innerHTML = `
                <div class="whisper-bubble">
                    <div class="whisper-sender-tag">
                        ${isMe ? 'Вы шепчете' : 'Шёпот от ' + this.escapeHtml(msg.sender_name)}:
                    </div>
                    <div class="whisper-text">${this.escapeHtml(msg.text)}</div>
                    <span class="whisper-time">${timeStr}</span>
                </div>
            `;
            box.appendChild(row);
            box.scrollTop = box.scrollHeight;
        }
    }

    async sendWhisper() {
        if (!this.activeWhisperFriendId || !window.currentUser) return;
        const input = document.getElementById('whisper-input-text');
        if (!input) return;
        const text = input.value.trim();
        if (!text) return;

        const friendId = this.activeWhisperFriendId;
        try {
            const res = await fetch(`/api/whispers/${friendId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            const data = await res.json();
            if (data.success) {
                input.value = '';
                this.appendWhisperMessage(friendId, data.message);
                if (window.tavernAudio) window.tavernAudio.playWhisper();
            } else if (data.error) {
                alert(data.error);
            }
        } catch(e){
            console.error(e);
        }
    }

    handleIncomingWhisper(msg) {
        const isFromFriend = msg.sender_id !== window.currentUser.id;
        const friendId = isFromFriend ? msg.sender_id : msg.receiver_id;
        const friendName = msg.sender_name;

        if (!this.activeWhispers[friendId]) {
            this.activeWhispers[friendId] = {
                name: friendName,
                lastId: 0,
                messages: []
            };
        }

        if (this.activeWhisperFriendId === friendId) {
            this.appendWhisperMessage(friendId, msg);
        } else {
            // Unread
            if (window.tavernAudio) window.tavernAudio.playWhisper();
            this.updateGlobalWhisperBadge(1);
        }
        this.renderWhisperTabs();
    }

    renderWhisperTabs() {
        const tabsContainer = document.getElementById('whisper-tabs-list');
        if (!tabsContainer) return;

        const friendIds = Object.keys(this.activeWhispers);
        if (friendIds.length === 0) {
            tabsContainer.innerHTML = '';
            return;
        }

        tabsContainer.innerHTML = friendIds.map(fid => {
            const id = parseInt(fid);
            const w = this.activeWhispers[id];
            const isActive = this.activeWhisperFriendId === id;
            return `
                <div class="whisper-tab ${isActive ? 'active' : ''}" onclick="tavernChat.openWhisper(${id}, '${tavernChat.escapeJs(w.name)}')">
                    <span>${this.escapeHtml(w.name)}</span>
                    <button class="whisper-tab-close" onclick="event.stopPropagation(); tavernChat.closeWhisperTab(${id})">×</button>
                </div>
            `;
        }).join('');
    }

    closeWhisperTab(friendId) {
        delete this.activeWhispers[friendId];
        const remaining = Object.keys(this.activeWhispers);
        if (remaining.length > 0) {
            const nextId = parseInt(remaining[0]);
            this.openWhisper(nextId, this.activeWhispers[nextId].name);
        } else {
            this.activeWhisperFriendId = null;
            const dock = document.getElementById('whisper-dock');
            if (dock) dock.classList.add('hidden');
        }
    }

    closeWhisperDock() {
        const dock = document.getElementById('whisper-dock');
        if (dock) dock.classList.add('hidden');
        this.activeWhisperFriendId = null;
    }

    updateGlobalWhisperBadge(count) {
        const badge = document.getElementById('whisper-badge-nav');
        if (badge) {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'inline-flex';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    escapeJs(str) {
        if (!str) return '';
        return String(str).replace(/'/g, "\\'").replace(/"/g, '\\"');
    }
}

window.tavernChat = new TavernChatManager();
