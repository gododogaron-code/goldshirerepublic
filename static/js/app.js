// WoW Forever 1.0 — the goldshire republick
// Streamlined Voting & Countdown Application

let currentTargetFaction = 'alliance';

document.addEventListener('DOMContentLoaded', async () => {
    initEmbersCanvas();
    initTelegramIntegration();
    await loadSettings();
    await loadFactions();
    updateUserVoteBadge();
});

// --- TELEGRAM MINI APP INTEGRATION ---
function initTelegramIntegration() {
    if (!window.Telegram || !window.Telegram.WebApp) return;
    const tg = window.Telegram.WebApp;
    try {
        tg.ready();
        tg.expand();
        if (typeof tg.setHeaderColor === 'function') tg.setHeaderColor('#09070b');
        if (typeof tg.setBackgroundColor === 'function') tg.setBackgroundColor('#09070b');
    } catch(e) {}

    // Pre-fill name from Telegram if not set
    const tgUser = tg.initDataUnsafe?.user;
    if (tgUser && !localStorage.getItem('voter_name')) {
        const fullName = `${tgUser.first_name || ''} ${tgUser.last_name || ''}`.trim();
        if (fullName) {
            localStorage.setItem('voter_name', fullName);
        }
    }
}

function triggerHaptic(type = 'light') {
    try {
        if (window.Telegram?.WebApp?.HapticFeedback) {
            window.Telegram.WebApp.HapticFeedback.impactOccurred(type);
        }
    } catch(e) {}
}

// --- PARTICLES BACKGROUND ---
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
    const maxParticles = 30;

    class Ember {
        constructor() { this.reset(true); }
        reset(initial = false) {
            this.x = Math.random() * width;
            this.y = initial ? Math.random() * height : height + 10;
            this.size = 1 + Math.random() * 2;
            this.speedY = 0.3 + Math.random() * 0.7;
            this.speedX = (Math.random() - 0.5) * 0.4;
            this.opacity = 0.15 + Math.random() * 0.4;
            this.fadeRate = 0.0015 + Math.random() * 0.0025;
            this.color = Math.random() > 0.4 ? '#eab308' : (Math.random() > 0.5 ? '#f97316' : '#d946ef');
        }
        update() {
            this.y -= this.speedY;
            this.x += this.speedX + Math.sin(this.y * 0.015) * 0.25;
            this.opacity -= this.fadeRate;
            if (this.opacity <= 0 || this.y < -10) this.reset();
        }
        draw() {
            ctx.save();
            ctx.globalAlpha = Math.max(0, this.opacity);
            ctx.fillStyle = this.color;
            ctx.shadowBlur = 8;
            ctx.shadowColor = this.color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }

    for (let i = 0; i < maxParticles; i++) particles.push(new Ember());

    function animate() {
        ctx.clearRect(0, 0, width, height);
        particles.forEach(p => { p.update(); p.draw(); });
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

        if (settings.countdown_target && window.wowCountdown) {
            window.wowCountdown.init(settings.countdown_target);
        }
    } catch(e) {
        console.error('Failed to load settings', e);
    }
}

// --- VOTER TOKEN UTILITY ---
function getVoterToken() {
    let token = localStorage.getItem('voter_token');
    if (!token) {
        token = 'voter_' + Math.random().toString(36).substring(2, 12) + Date.now().toString(36);
        localStorage.setItem('voter_token', token);
    }
    return token;
}

// --- FACTIONS & VOTING ---
async function loadFactions() {
    try {
        const res = await fetch('/api/factions');
        const data = await res.json();
        renderFactionsUI(data);
    } catch(e) {
        console.error('Error loading factions', e);
    }
}

function renderFactionsUI(data) {
    const counts = data.counts || { alliance: 0, horde: 0, the_world: 0 };
    const pcts = data.percentages || { alliance: 0, horde: 0, the_world: 0 };
    const rosters = data.roster || { alliance: [], horde: [], the_world: [] };

    // Update counts
    const elCountAlliance = document.getElementById('count-alliance');
    const elCountWorld = document.getElementById('count-world');
    const elCountHorde = document.getElementById('count-horde');
    if (elCountAlliance) elCountAlliance.textContent = counts.alliance;
    if (elCountWorld) elCountWorld.textContent = counts.the_world;
    if (elCountHorde) elCountHorde.textContent = counts.horde;

    // Update percentages
    const elPctAlliance = document.getElementById('pct-alliance');
    const elPctWorld = document.getElementById('pct-world');
    const elPctHorde = document.getElementById('pct-horde');
    if (elPctAlliance) elPctAlliance.textContent = `${pcts.alliance}%`;
    if (elPctWorld) elPctWorld.textContent = `${pcts.the_world}%`;
    if (elPctHorde) elPctHorde.textContent = `${pcts.horde}%`;

    // Update balance bar
    const barAlliance = document.getElementById('balance-bar-alliance');
    const barWorld = document.getElementById('balance-bar-world');
    const barHorde = document.getElementById('balance-bar-horde');
    if (barAlliance) barAlliance.style.width = `${Math.max(4, pcts.alliance)}%`;
    if (barWorld) barWorld.style.width = `${Math.max(4, pcts.the_world)}%`;
    if (barHorde) barHorde.style.width = `${Math.max(4, pcts.horde)}%`;

    // Render Rosters
    renderRosterList('roster-list-alliance', 'roster-count-alliance', rosters.alliance);
    renderRosterList('roster-list-the_world', 'roster-count-the_world', rosters.the_world);
    renderRosterList('roster-list-horde', 'roster-count-horde', rosters.horde);

    // Highlight user's chosen card
    highlightUserVote();
}

const CLASS_RU_NAMES = {
    warrior: 'Воин', paladin: 'Паладин', hunter: 'Охотник', rogue: 'Разбойник',
    priest: 'Жрец', shaman: 'Шаман', mage: 'Маг', warlock: 'Чернокнижник', druid: 'Друид'
};

function renderRosterList(listId, countId, players) {
    const listEl = document.getElementById(listId);
    const countEl = document.getElementById(countId);
    if (!listEl) return;

    if (countEl) countEl.textContent = players.length;

    if (!players || players.length === 0) {
        listEl.innerHTML = '<div class="roster-empty">Пока никто не выбрал эту сторону. Будьте первыми!</div>';
        return;
    }

    const myName = (localStorage.getItem('voter_name') || '').toLowerCase().trim();

    listEl.innerHTML = players.map(p => {
        const cls = p.wow_class || 'warrior';
        const isMe = myName && p.character_name.toLowerCase().trim() === myName;
        return `
            <div class="roster-card ${isMe ? 'roster-card-me' : ''}">
                <div class="roster-class-icon-wrap">
                    <img src="/static/images/classes/${cls}.png" alt="${cls}" class="roster-class-icon" onerror="this.style.display='none'">
                </div>
                <div class="roster-info">
                    <div class="roster-top-row">
                        <span class="roster-name class-color-${cls}">${escapeHtml(p.character_name)}</span>
                        ${isMe ? '<span class="roster-you-badge">ВЫ</span>' : ''}
                    </div>
                    <span class="roster-meta class-color-${cls}">${CLASS_RU_NAMES[cls] || cls}</span>
                </div>
            </div>
        `;
    }).join('');
}

function highlightUserVote() {
    const myFaction = localStorage.getItem('voter_faction');
    ['alliance', 'the_world', 'horde'].forEach(f => {
        const card = document.getElementById(`card-${f}`);
        const btn = document.getElementById(`vote-btn-${f}`);
        if (card) {
            if (f === myFaction) {
                card.classList.add('voted-active');
            } else {
                card.classList.remove('voted-active');
            }
        }
        if (btn) {
            if (f === myFaction) {
                btn.classList.add('btn-chosen');
                btn.innerHTML = '✔ Ваш выбор';
            } else {
                btn.classList.remove('btn-chosen');
                if (f === 'alliance') btn.textContent = 'Тусить в Златоземье';
                if (f === 'the_world') btn.textContent = 'Не буду играть';
                if (f === 'horde') btn.textContent = 'Контролировать Златоземье';
            }
        }
    });
}

function updateUserVoteBadge() {
    const badge = document.getElementById('nav-user-vote-badge');
    const text = document.getElementById('nav-user-vote-text');
    const faction = localStorage.getItem('voter_faction');
    const name = localStorage.getItem('voter_name');

    if (badge && text && faction) {
        badge.style.display = 'inline-flex';
        const labels = {
            alliance: 'Альянс 🦁',
            the_world: 'Не играю ⚪',
            horde: 'Орда ⚔️'
        };
        text.textContent = `${name ? name + ' • ' : ''}${labels[faction] || 'Голос отдан'}`;
    }
}

// --- VOTE MODAL ACTIONS ---
function openVoteModal(faction) {
    currentTargetFaction = faction;
    triggerHaptic('light');

    const modal = document.getElementById('modal-vote');
    const crest = document.getElementById('vote-modal-crest');
    const title = document.getElementById('vote-modal-title');
    const desc = document.getElementById('vote-modal-desc');
    const factionInput = document.getElementById('vote-faction-input');
    const nameInput = document.getElementById('vote-name-input');

    if (!modal) return;

    factionInput.value = faction;

    if (faction === 'alliance') {
        crest.src = '/static/images/factions/alliance.png?v=2';
        title.textContent = 'АЛЬЯНС 🦁';
        desc.textContent = '«Чтобы тусить в Златоземье»';
    } else if (faction === 'horde') {
        crest.src = '/static/images/factions/horde.png?v=2';
        title.textContent = 'ОРДА ⚔️';
        desc.textContent = '«Чтобы контролировать Златоземье»';
    } else {
        crest.src = '/static/images/factions/no_play.svg';
        title.textContent = 'НЕ БУДУ ИГРАТЬ ⚪';
        desc.textContent = '«Останусь дома в Златоземье»';
    }

    // Pre-fill previously entered name if available
    const savedName = localStorage.getItem('voter_name') || '';
    if (nameInput) {
        nameInput.value = savedName;
    }

    // Pre-select previously chosen class
    const savedClass = localStorage.getItem('voter_class') || 'warrior';
    const radio = document.querySelector(`input[name="vote-class"][value="${savedClass}"]`);
    if (radio) radio.checked = true;

    modal.style.display = 'flex';
    setTimeout(() => { if (nameInput) nameInput.focus(); }, 100);
}

function closeVoteModal() {
    const modal = document.getElementById('modal-vote');
    if (modal) modal.style.display = 'none';
}

async function handleVoteSubmit(e) {
    e.preventDefault();
    const nameInput = document.getElementById('vote-name-input');
    const factionInput = document.getElementById('vote-faction-input');
    const classInput = document.querySelector('input[name="vote-class"]:checked');
    const submitBtn = document.getElementById('vote-submit-btn');

    const characterName = (nameInput?.value || '').trim();
    const faction = factionInput?.value || currentTargetFaction;
    const wowClass = classInput?.value || 'warrior';

    if (!characterName || characterName.length < 2) {
        alert('Пожалуйста, введите имя или игровой ник (от 2 символов)');
        return;
    }

    const voterToken = getVoterToken();

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Сохранение...';
    }

    try {
        const res = await fetch('/api/vote', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                character_name: characterName,
                faction: faction,
                wow_class: wowClass,
                voter_token: voterToken
            })
        });

        const data = await res.json();
        if (data.success) {
            triggerHaptic('medium');
            localStorage.setItem('voter_name', characterName);
            localStorage.setItem('voter_faction', faction);
            localStorage.setItem('voter_class', wowClass);

            closeVoteModal();
            updateUserVoteBadge();
            await loadFactions();

            if (window.tavernAudio) window.tavernAudio.playClick();
        } else {
            alert(data.error || 'Ошибка при сохранении голоса');
        }
    } catch(err) {
        alert('Ошибка связи с сервером при голосовании');
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Подтвердить голос';
        }
    }
}

function scrollToFactions() {
    const el = document.getElementById('factions-section');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
}

function escapeHtml(str) {
    return (str || '').replace(/[&<>"']/g, m => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
    })[m]);
}
