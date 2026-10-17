// Main Application Coordinator for WoW Forever 1.0 — The World & the goldshire republick
window.currentUser = null;
window.currentFactionsData = null;

function getAvatarSrc(avatar) {
    if (!avatar) return '/static/images/avatars/human_male.svg';
    if (avatar.startsWith('/') || avatar.startsWith('http://') || avatar.startsWith('https://')) {
        return avatar;
    }
    return `/static/images/avatars/${avatar}.svg`;
}

document.addEventListener('DOMContentLoaded', async () => {
    applyCachedUserUI();
    initEmbersCanvas();
    await initTelegramApp();
    await checkAuth();
    await loadSettings();
    await loadFactions();
    window.tavernChat.init();
    setupGlobalEvents();
    setupAvatarUploaders();
});

// --- TELEGRAM MINI APP INTEGRATION ---
async function initTelegramApp() {
    if (!window.Telegram || !window.Telegram.WebApp) return;
    const tg = window.Telegram.WebApp;
    try {
        tg.ready();
        tg.expand();
        if (typeof tg.setHeaderColor === 'function') tg.setHeaderColor('#09070b');
        if (typeof tg.setBackgroundColor === 'function') tg.setBackgroundColor('#09070b');
    } catch (e) {
        console.warn("Telegram WebApp initialization:", e);
    }

    const tgUser = tg.initDataUnsafe?.user;
    if (tgUser) {
        console.log("Telegram user identified:", tgUser);
        try {
            const res = await fetch('/api/telegram_auth', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tg_user: tgUser })
            });
            const data = await res.json();
            if (data.success && data.user) {
                window.currentUser = data.user;
                updateUserUI();
            }
        } catch (err) {
            console.error("Telegram auto-auth error:", err);
        }
    }
}

// --- AMBIENT PARTICLES (Minimalist realistic ember/stardust glow) ---
function initEmbersCanvas() {
    const canvas = document.getElementById('embers-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let width = canvas.width = canvas.parentElement.offsetWidth;
    let height = canvas.height = canvas.parentElement.offsetHeight;

    window.addEventListener('resize', () => {
        width = canvas.width = canvas.parentElement.offsetWidth;
        height = canvas.height = canvas.parentElement.offsetHeight;
    });

    const particles = [];
    const maxParticles = 35;

    class Ember {
        constructor() {
            this.reset(true);
        }

        reset(initial = false) {
            this.x = Math.random() * width;
            this.y = initial ? Math.random() * height : height + 10;
            this.size = 1 + Math.random() * 2.2;
            this.speedY = 0.3 + Math.random() * 0.8;
            this.speedX = (Math.random() - 0.5) * 0.5;
            this.opacity = 0.15 + Math.random() * 0.5;
            this.fadeRate = 0.0015 + Math.random() * 0.003;
            this.color = Math.random() > 0.4 ? '#eab308' : (Math.random() > 0.5 ? '#f97316' : '#d946ef');
        }

        update() {
            this.y -= this.speedY;
            this.x += this.speedX + Math.sin(this.y * 0.015) * 0.3;
            this.opacity -= this.fadeRate;

            if (this.opacity <= 0 || this.y < -10) {
                this.reset();
            }
        }

        draw() {
            ctx.save();
            ctx.globalAlpha = Math.max(0, this.opacity);
            ctx.shadowBlur = 6;
            ctx.shadowColor = this.color;
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }

    for (let i = 0; i < maxParticles; i++) {
        particles.push(new Ember());
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);
        particles.forEach(p => {
            p.update();
            p.draw();
        });
        requestAnimationFrame(animate);
    }
    animate();
}

// --- SETTINGS & COUNTDOWN ---
async function loadSettings() {
    try {
        const res = await fetch('/api/settings');
        const settings = await res.json();
        
        const titleEl = document.getElementById('hero-server-title');
        const subTitleEl = document.getElementById('hero-server-subtitle');
        const infoEl = document.getElementById('hero-server-info');
        const welcomeEl = document.getElementById('tavern-welcome-quote');
        const guildEl = document.getElementById('guild-brand-name');

        if (titleEl && settings.server_title) titleEl.textContent = settings.server_title;
        if (subTitleEl && settings.server_subtitle) subTitleEl.textContent = settings.server_subtitle;
        if (infoEl && settings.server_info) infoEl.textContent = settings.server_info;
        if (welcomeEl && settings.tavern_welcome) welcomeEl.textContent = `«${settings.tavern_welcome}»`;
        if (guildEl && settings.guild_name) guildEl.textContent = settings.guild_name;

        if (settings.countdown_target) {
            window.wowCountdown.init(settings.countdown_target);
            const dateInput = document.getElementById('admin-countdown-date');
            if (dateInput) {
                const d = new Date(settings.countdown_target);
                const localISO = new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
                dateInput.value = localISO;
            }
        }

        const titleInput = document.getElementById('admin-server-title');
        const subInput = document.getElementById('admin-server-subtitle');
        const infoInput = document.getElementById('admin-server-info');
        if (titleInput) titleInput.value = settings.server_title || '';
        if (subInput) subInput.value = settings.server_subtitle || '';
        if (infoInput) infoInput.value = settings.server_info || '';
    } catch(e) {
        console.error('Failed to load settings', e);
    }
}

// --- AUTHENTICATION ---
async function checkAuth() {
    try {
        const res = await fetch('/api/me');
        const data = await res.json();
        window.currentUser = data.user;
        updateUserUI();
    } catch(e) {
        window.currentUser = null;
        updateUserUI();
    }
}

function applyCachedUserUI() {
    try {
        const cached = localStorage.getItem('goldshire_user');
        if (cached) {
            const user = JSON.parse(cached);
            const guestNav = document.getElementById('nav-guest-actions');
            const userNav = document.getElementById('nav-user-actions');
            const userAvatarImg = document.getElementById('nav-user-avatar');
            const userNameSpan = document.getElementById('nav-user-name');
            const adminBtn = document.getElementById('nav-admin-btn');
            if (guestNav) guestNav.style.display = 'none';
            if (userNav) userNav.style.display = 'flex';
            if (userNameSpan && user.character_name) {
                userNameSpan.textContent = user.character_name;
                userNameSpan.className = `class-color-${user.wow_class || 'warrior'}`;
            }
            if (userAvatarImg && user.avatar) {
                userAvatarImg.src = getAvatarSrc(user.avatar);
            }
            if (adminBtn) {
                adminBtn.style.display = user.is_admin ? 'inline-flex' : 'none';
            }
        }
    } catch(e) {}
}

function updateUserUI() {
    const guestNav = document.getElementById('nav-guest-actions');
    const userNav = document.getElementById('nav-user-actions');
    const userAvatarImg = document.getElementById('nav-user-avatar');
    const userNameSpan = document.getElementById('nav-user-name');
    const adminBtn = document.getElementById('nav-admin-btn');

    if (window.currentUser) {
        try {
            localStorage.setItem('goldshire_user', JSON.stringify({
                character_name: window.currentUser.character_name,
                wow_class: window.currentUser.wow_class,
                avatar: window.currentUser.avatar,
                is_admin: window.currentUser.is_admin
            }));
        } catch(e) {}

        if (guestNav) guestNav.style.display = 'none';
        if (userNav) userNav.style.display = 'flex';
        if (userNameSpan) {
            userNameSpan.textContent = window.currentUser.character_name;
            userNameSpan.className = `class-color-${window.currentUser.wow_class}`;
        }
        if (userAvatarImg) {
            userAvatarImg.src = getAvatarSrc(window.currentUser.avatar);
        }
        if (adminBtn) {
            adminBtn.style.display = window.currentUser.is_admin ? 'inline-flex' : 'none';
        }
    } else {
        try {
            localStorage.removeItem('goldshire_user');
        } catch(e) {}

        if (guestNav) guestNav.style.display = 'flex';
        if (userNav) userNav.style.display = 'none';
        if (adminBtn) adminBtn.style.display = 'none';
    }
}

// --- FACTIONS & VOTING ---
async function loadFactions() {
    try {
        const res = await fetch('/api/factions');
        const data = await res.json();
        window.currentFactionsData = data;
        renderFactionsUI(data);
    } catch(e) {
        console.error('Error loading factions', e);
    }
}

function renderFactionsUI(data) {
    // 1. Balance bar
    const barAlliance = document.getElementById('balance-bar-alliance');
    const barHorde = document.getElementById('balance-bar-horde');
    const barWorld = document.getElementById('balance-bar-world');

    const pctAlliance = data.percentages.alliance || 0;
    const pctHorde = data.percentages.horde || 0;
    const pctWorld = data.percentages.the_world || 0;

    if (barAlliance) {
        barAlliance.style.width = `${pctAlliance}%`;
        barAlliance.textContent = pctAlliance > 10 ? `${pctAlliance}%` : '';
    }
    if (barHorde) {
        barHorde.style.width = `${pctHorde}%`;
        barHorde.textContent = pctHorde > 10 ? `${pctHorde}%` : '';
    }
    if (barWorld) {
        barWorld.style.width = `${pctWorld}%`;
        barWorld.textContent = pctWorld > 10 ? `${pctWorld}%` : '';
    }

    // 2. Count numbers
    const cntAll = document.getElementById('count-alliance');
    const cntHorde = document.getElementById('count-horde');
    const cntWorld = document.getElementById('count-world');

    if (cntAll) cntAll.textContent = data.counts.alliance;
    if (cntHorde) cntHorde.textContent = data.counts.horde;
    if (cntWorld) cntWorld.textContent = data.counts.the_world;

    // 3. Highlight user's chosen vote button
    ['alliance', 'horde', 'the_world'].forEach(fac => {
        const btn = document.getElementById(`vote-btn-${fac}`);
        if (btn) {
            const userFac = window.currentUser ? (window.currentUser.faction === 'tavern' ? 'the_world' : window.currentUser.faction) : null;
            if (userFac === fac) {
                btn.classList.add('selected-vote');
                btn.innerHTML = `<span class="vote-check">✓</span> Ваш выбор`;
            } else {
                btn.classList.remove('selected-vote');
                const defaultLabels = {
                    'alliance': 'Тусить в Златоземье',
                    'horde': 'Контролировать Златоземье',
                    'the_world': 'Не буду играть'
                };
                btn.textContent = defaultLabels[fac];
            }
        }
    });

    // 4. Render Rosters
    renderRosterList('alliance', data.roster.alliance);
    renderRosterList('horde', data.roster.horde);
    renderRosterList('the_world', data.roster.the_world);
}

function renderRosterList(faction, members) {
    const container = document.getElementById(`roster-list-${faction}`);
    if (!container) return;

    if (!members || members.length === 0) {
        container.innerHTML = `<div class="roster-empty">Список пока пуст. Будьте первыми!</div>`;
        return;
    }

    container.innerHTML = members.map(m => {
        const isMe = window.currentUser && window.currentUser.id === m.id;
        return `
            <div class="roster-card faction-border-${faction}">
                <div class="roster-avatar-wrap">
                    <img src="${getAvatarSrc(m.avatar)}" alt="${m.character_name}" class="roster-avatar-img"/>
                    <img src="/static/images/classes/${m.wow_class}.svg" class="roster-class-icon" title="${m.wow_class}" />
                </div>
                <div class="roster-info">
                    <div class="roster-top-row">
                        <span class="roster-name class-color-${m.wow_class}">${escapeHtml(m.character_name)}</span>
                        ${isMe ? '<span class="roster-you-badge">Это вы</span>' : ''}
                    </div>
                    <div class="roster-meta">${escapeHtml(m.race)} • ${getRuClassName(m.wow_class)}</div>
                </div>
                ${!isMe ? `
                    <button class="roster-whisper-btn" onclick="tavernChat.openWhisper(${m.id}, '${escapeJs(m.character_name)}')">
                        💬 Шепнуть
                    </button>
                ` : ''}
            </div>
        `;
    }).join('');
}

async function castVote(faction) {
    if (!window.currentUser) {
        showAuthModal('login');
        return;
    }

    try {
        const res = await fetch('/api/vote', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ faction })
        });
        const data = await res.json();
        if (data.success) {
            window.currentUser.faction = faction;
            if (window.tavernAudio) {
                window.tavernAudio.playVoteFanfare(faction);
            }
            await loadFactions();
        } else if (data.error) {
            alert(data.error);
        }
    } catch(e) {
        console.error(e);
    }
}

// --- NOTICE BOARD ---
async function loadBoardPosts() {
    try {
        const res = await fetch('/api/board');
        const posts = await res.json();
        renderBoardPosts(posts);
    } catch(e){
        console.error(e);
    }
}

function renderBoardPosts(posts) {
    const container = document.getElementById('board-posts-container');
    if (!container) return;

    if (!posts || posts.length === 0) {
        container.innerHTML = `<div class="board-empty-hint">Доска объявлений пуста. Напишите первое объявление о планах на открытие! 📜</div>`;
        return;
    }

    const categoryBadges = {
        'plans': '🎯 Планы на старт',
        'guild': '🛡️ the goldshire republick',
        'general': '💬 Разговоры',
        'memes': '🎭 Мемы и скриншоты'
    };

    container.innerHTML = posts.map(p => {
        const dateStr = p.created_at ? new Date(p.created_at).toLocaleDateString([], {day: 'numeric', month: 'short', hour:'2-digit', minute:'2-digit'}) : '';
        return `
            <div class="board-card parchment-paper" id="board-post-${p.id}">
                <div class="board-card-header">
                    <span class="board-cat-badge">${categoryBadges[p.category] || '📜 Объявление'}</span>
                    <span class="board-card-date">${dateStr}</span>
                </div>
                <h3 class="board-card-title">${escapeHtml(p.title)}</h3>
                <div class="board-card-content">${escapeHtml(p.content).replace(/\n/g, '<br>')}</div>
                <div class="board-card-footer">
                    <div class="board-author-info">
                        <img src="${getAvatarSrc(p.avatar)}" class="board-author-avatar" />
                        <span class="class-color-${p.wow_class}">${escapeHtml(p.character_name)}</span>
                    </div>
                    <button class="board-comments-toggle-btn" onclick="toggleComments(${p.id})">
                        💬 Комментарии (${p.comment_count})
                    </button>
                </div>
                <div class="board-comments-section hidden" id="comments-section-${p.id}">
                    <div class="board-comments-list" id="comments-list-${p.id}">
                        <div class="loading-spin">Загрузка комментариев...</div>
                    </div>
                    <div class="board-add-comment-row">
                        <input type="text" id="comment-input-${p.id}" class="site-input comment-input" placeholder="Оставить комментарий..." onkeydown="if(event.key==='Enter') submitComment(${p.id})"/>
                        <button class="site-btn site-btn-small" onclick="submitComment(${p.id})">Ответить</button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

async function toggleComments(postId) {
    const section = document.getElementById(`comments-section-${postId}`);
    if (!section) return;

    section.classList.toggle('hidden');
    if (!section.classList.contains('hidden')) {
        await loadPostComments(postId);
    }
}

async function loadPostComments(postId) {
    const list = document.getElementById(`comments-list-${postId}`);
    if (!list) return;

    try {
        const res = await fetch(`/api/board/${postId}/comments`);
        const comments = await res.json();

        if (!comments || comments.length === 0) {
            list.innerHTML = `<div class="no-comments-hint">Комментариев пока нет. Будьте первыми!</div>`;
            return;
        }

        list.innerHTML = comments.map(c => {
            const timeStr = c.created_at ? new Date(c.created_at).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}) : '';
            return `
                <div class="comment-item">
                    <img src="${getAvatarSrc(c.avatar)}" class="comment-avatar" />
                    <div class="comment-body">
                        <div class="comment-head">
                            <span class="class-color-${c.wow_class}">${escapeHtml(c.character_name)}</span>
                            <span class="comment-time">${timeStr}</span>
                        </div>
                        <div class="comment-text">${escapeHtml(c.content)}</div>
                    </div>
                </div>
            `;
        }).join('');
    } catch(e){
        list.innerHTML = `<div class="error-hint">Ошибка загрузки заметок</div>`;
    }
}

async function submitComment(postId) {
    if (!window.currentUser) {
        showAuthModal('login');
        return;
    }

    const input = document.getElementById(`comment-input-${postId}`);
    if (!input) return;
    const content = input.value.trim();
    if (!content) return;

    try {
        const res = await fetch(`/api/board/${postId}/comments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });
        const data = await res.json();
        if (data.success) {
            input.value = '';
            if (window.tavernAudio) window.tavernAudio.playClick();
            await loadPostComments(postId);
        } else if (data.error) {
            alert(data.error);
        }
    } catch(e){
        console.error(e);
    }
}

async function createNewBoardPost() {
    if (!window.currentUser) {
        showAuthModal('login');
        return;
    }

    const titleInput = document.getElementById('new-post-title');
    const catInput = document.getElementById('new-post-category');
    const contentInput = document.getElementById('new-post-content');

    if (!titleInput || !contentInput) return;
    const title = titleInput.value.trim();
    const category = catInput ? catInput.value : 'plans';
    const content = contentInput.value.trim();

    if (!title) {
        alert('Укажите тему объявления!');
        return;
    }
    if (!content) {
        alert('Напишите текст сообщения!');
        return;
    }

    try {
        const res = await fetch('/api/board', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, category, content })
        });
        const data = await res.json();
        if (data.success) {
            titleInput.value = '';
            contentInput.value = '';
            closeModal('modal-new-post');
            if (window.tavernAudio) window.tavernAudio.playClick();
            await loadBoardPosts();
        } else if (data.error) {
            alert(data.error);
        }
    } catch(e){
        console.error(e);
    }
}

// --- AVATAR UPLOADERS & PREVIEW ---
function setupAvatarUploaders() {
    ['reg', 'prof'].forEach(prefix => {
        const fileInput = document.getElementById(`${prefix}-avatar-file`);
        const urlInput = document.getElementById(`${prefix}-avatar-url`);
        const valInput = document.getElementById(`${prefix}-avatar-val`);
        const preview = document.getElementById(`${prefix}-avatar-preview`);

        if (fileInput) {
            fileInput.addEventListener('change', async (e) => {
                const file = e.target.files[0];
                if (!file) return;

                const formData = new FormData();
                formData.append('avatar', file);

                try {
                    const statusText = document.getElementById(`${prefix}-avatar-status`);
                    if (statusText) statusText.textContent = 'Загрузка аватара...';

                    const res = await fetch('/api/upload_avatar', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json().catch(() => ({}));
                    if (res.ok && data.success && data.avatar_url) {
                        valInput.value = data.avatar_url;
                        if (preview) preview.src = data.avatar_url;
                        if (urlInput) urlInput.value = '';
                        if (statusText) statusText.textContent = 'Аватар успешно загружен!';
                        const picker = document.getElementById(`${prefix}-avatar-picker`);
                        if (picker) picker.querySelectorAll('.avatar-option').forEach(o => o.classList.remove('selected'));
                        if (window.tavernAudio) window.tavernAudio.playClick();
                    } else {
                        if (statusText) statusText.textContent = '';
                        alert(data.error || `Ошибка загрузки аватара (код ${res.status})`);
                    }
                } catch(err) {
                    const statusText = document.getElementById(`${prefix}-avatar-status`);
                    if (statusText) statusText.textContent = '';
                    alert('Ошибка связи с сервером при загрузке: ' + (err.message || err));
                }
            });
        }

        if (urlInput) {
            urlInput.addEventListener('input', (e) => {
                const url = e.target.value.trim();
                if (url) {
                    valInput.value = url;
                    if (preview) preview.src = url;
                    const picker = document.getElementById(`${prefix}-avatar-picker`);
                    if (picker) picker.querySelectorAll('.avatar-option').forEach(o => o.classList.remove('selected'));
                }
            });
        }
    });

    populateAvatarPickers();
}

function populateAvatarPickers() {
    // Only Classic Vanilla 1.0 races (Human, Dwarf, Night Elf, Gnome, Orc, Undead, Tauren, Troll)
    const vanillaAvatars = [
        'human_male', 'human_female', 'dwarf', 'nightelf', 'gnome',
        'orc', 'undead', 'tauren', 'troll'
    ];

    ['reg-avatar-picker', 'prof-avatar-picker'].forEach(pickerId => {
        const picker = document.getElementById(pickerId);
        if (!picker) return;

        picker.innerHTML = vanillaAvatars.map((a, i) => `
            <div class="avatar-option ${i === 0 ? 'selected' : ''}" data-avatar="${a}" onclick="selectAvatarOption('${pickerId}', '${a}', this)">
                <img src="/static/images/avatars/${a}.svg" alt="${a}" />
            </div>
        `).join('');
    });
}

function selectAvatarOption(pickerId, avatarName, el) {
    const picker = document.getElementById(pickerId);
    if (!picker) return;
    picker.querySelectorAll('.avatar-option').forEach(o => o.classList.remove('selected'));
    el.classList.add('selected');

    const prefix = pickerId.startsWith('reg') ? 'reg' : 'prof';
    const hiddenInput = document.getElementById(`${prefix}-avatar-val`);
    const preview = document.getElementById(`${prefix}-avatar-preview`);
    const urlInput = document.getElementById(`${prefix}-avatar-url`);

    if (hiddenInput) hiddenInput.value = avatarName;
    if (preview) preview.src = `/static/images/avatars/${avatarName}.svg`;
    if (urlInput) urlInput.value = '';

    if (window.tavernAudio) window.tavernAudio.playClick();
}

// --- MODALS & GLOBAL EVENTS ---
function setupGlobalEvents() {
    const audioBtn = document.getElementById('audio-toggle-btn');
    if (audioBtn) {
        audioBtn.addEventListener('click', () => {
            window.tavernAudio.toggleMusic();
        });
    }

    document.querySelectorAll('.modal-overlay').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.add('hidden');
            }
        });
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay').forEach(m => m.classList.add('hidden'));
        }
    });
}

// --- AUTH MODALS ---
function showAuthModal(type = 'login') {
    const loginForm = document.getElementById('modal-login-section');
    const regForm = document.getElementById('modal-register-section');
    const modal = document.getElementById('modal-auth');

    if (!modal) return;
    modal.classList.remove('hidden');

    if (type === 'login') {
        if (loginForm) loginForm.style.display = 'block';
        if (regForm) regForm.style.display = 'none';
        document.getElementById('auth-tab-login').classList.add('active');
        document.getElementById('auth-tab-reg').classList.remove('active');
    } else {
        if (loginForm) loginForm.style.display = 'none';
        if (regForm) regForm.style.display = 'block';
        document.getElementById('auth-tab-login').classList.remove('active');
        document.getElementById('auth-tab-reg').classList.add('active');
    }
}

async function handleLoginSubmit(e) {
    e.preventDefault();
    const u = document.getElementById('login-username').value.trim();
    const p = document.getElementById('login-password').value.trim();

    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: u, password: p })
        });
        const data = await res.json();
        if (data.success) {
            window.currentUser = data.user;
            closeModal('modal-auth');
            updateUserUI();
            await loadFactions();
            window.tavernChat.initWhisperWebSocket();
            if (window.tavernAudio) window.tavernAudio.playClick();
        } else {
            alert(data.error || 'Ошибка входа');
        }
    } catch(err) {
        alert('Ошибка связи с сервером');
    }
}

async function handleRegisterSubmit(e) {
    e.preventDefault();
    const username = document.getElementById('reg-username').value.trim();
    const password = document.getElementById('reg-password').value.trim();
    const charName = document.getElementById('reg-charname').value.trim() || username;
    const wowClass = document.getElementById('reg-class').value;
    const faction = document.getElementById('reg-faction').value;

    const raceEl = document.getElementById('reg-race');
    const defaultRace = faction === 'horde' ? 'Орк' : 'Человек';
    const race = raceEl ? raceEl.value : defaultRace;

    const avatarEl = document.getElementById('reg-avatar-val');
    const defaultAvatar = faction === 'horde' ? 'orc' : 'human_male';
    const avatar = (avatarEl && avatarEl.value) ? avatarEl.value : defaultAvatar;

    try {
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username, password, character_name: charName,
                wow_class: wowClass, race, faction,
                avatar
            })
        });
        const data = await res.json();
        if (data.success) {
            window.currentUser = data.user;
            closeModal('modal-auth');
            updateUserUI();
            await loadFactions();
            window.tavernChat.initWhisperWebSocket();
            if (window.tavernAudio) window.tavernAudio.playVoteFanfare(faction);
        } else {
            alert(data.error || 'Ошибка создания профиля');
        }
    } catch(err) {
        alert('Ошибка связи с сервером');
    }
}

async function handleLogout() {
    await fetch('/api/logout', { method: 'POST' });
    window.currentUser = null;
    updateUserUI();
    await loadFactions();
    window.location.reload();
}

// --- PROFILE MODAL ---
function openProfileModal() {
    if (!window.currentUser) return;
    const m = document.getElementById('modal-profile');
    if (!m) return;

    document.getElementById('prof-charname').value = window.currentUser.character_name;
    document.getElementById('prof-class').value = window.currentUser.wow_class;
    document.getElementById('prof-race').value = window.currentUser.race;
    const curFac = window.currentUser.faction === 'tavern' ? 'the_world' : window.currentUser.faction;
    document.getElementById('prof-faction').value = curFac;
    document.getElementById('prof-avatar-val').value = window.currentUser.avatar;

    const preview = document.getElementById('prof-avatar-preview');
    if (preview) {
        preview.src = getAvatarSrc(window.currentUser.avatar);
    }

    const picker = document.getElementById('prof-avatar-picker');
    if (picker) {
        picker.querySelectorAll('.avatar-option').forEach(o => {
            if (o.getAttribute('data-avatar') === window.currentUser.avatar) {
                o.classList.add('selected');
            } else {
                o.classList.remove('selected');
            }
        });
    }

    m.classList.remove('hidden');
}

async function handleProfileSave(e) {
    e.preventDefault();
    if (!window.currentUser) return;

    const charName = document.getElementById('prof-charname').value.trim();
    const wowClass = document.getElementById('prof-class').value;
    const race = document.getElementById('prof-race').value;
    const faction = document.getElementById('prof-faction').value;
    const avatar = document.getElementById('prof-avatar-val').value;
    const newPwd = document.getElementById('prof-new-password').value.trim();

    try {
        const res = await fetch('/api/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                character_name: charName,
                wow_class: wowClass,
                race, faction,
                avatar,
                new_password: newPwd
            })
        });
        const data = await res.json();
        if (data.success) {
            window.currentUser = data.user;
            closeModal('modal-profile');
            updateUserUI();
            await loadFactions();
            if (window.tavernAudio) window.tavernAudio.playClick();
        } else {
            alert(data.error || 'Ошибка обновления профиля');
        }
    } catch(err){
        alert('Ошибка сохранения');
    }
}

// --- ADMIN SETTINGS MODAL ---
function openAdminModal() {
    if (!window.currentUser || !window.currentUser.is_admin) return;
    const m = document.getElementById('modal-admin');
    if (m) m.classList.remove('hidden');
}

async function handleAdminSave(e) {
    e.preventDefault();
    const serverTitle = document.getElementById('admin-server-title').value.trim();
    const serverSubtitle = document.getElementById('admin-server-subtitle').value.trim();
    const serverInfo = document.getElementById('admin-server-info').value.trim();
    const dateVal = document.getElementById('admin-countdown-date').value;

    let countdown_target = '';
    if (dateVal) {
        countdown_target = new Date(dateVal).toISOString();
    }

    try {
        const res = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                server_title: serverTitle,
                server_subtitle: serverSubtitle,
                server_info: serverInfo,
                countdown_target: countdown_target
            })
        });
        const data = await res.json();
        if (data.success) {
            closeModal('modal-admin');
            await loadSettings();
            if (window.tavernAudio) window.tavernAudio.playClick();
        } else {
            alert(data.error || 'Ошибка сохранения настроек');
        }
    } catch(err){
        alert('Ошибка связи с сервером');
    }
}

function closeModal(modalId) {
    const m = document.getElementById(modalId);
    if (m) m.classList.add('hidden');
}

function openModal(modalId) {
    const m = document.getElementById(modalId);
    if (m) m.classList.remove('hidden');
}

function getRuClassName(cls) {
    // Vanilla 1.0 classes
    const names = {
        'warrior': 'Воин',
        'paladin': 'Паладин',
        'hunter': 'Охотник',
        'rogue': 'Разбойник',
        'priest': 'Жрец',
        'shaman': 'Шаман',
        'mage': 'Маг',
        'warlock': 'Чернокнижник',
        'druid': 'Друид'
    };
    return names[cls] || cls;
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function escapeJs(str) {
    if (!str) return '';
    return String(str).replace(/'/g, "\\'").replace(/"/g, '\\"');
}
