// Background Music & Audio Manager for WoW Forever — The World
class AudioManager {
    constructor() {
        this.bgAudio = new Audio('/static/audio/background_music.mp3');
        this.bgAudio.loop = true;
        this.bgAudio.volume = 0.55;
        this.isPlaying = false;
        this.ctx = null;
    }

    init() {
        if (this.ctx) return;
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {
            this.ctx = new AudioContext();
        }
    }

    toggleMusic() {
        this.init();
        if (this.ctx && this.ctx.state === 'suspended') {
            this.ctx.resume();
        }

        if (!this.isPlaying) {
            const playPromise = this.bgAudio.play();
            if (playPromise !== undefined) {
                playPromise.then(() => {
                    this.isPlaying = true;
                    this.updateButtonUI(true);
                }).catch(err => {
                    console.warn('Audio play restricted by browser:', err);
                    // Try re-triggering on next user click
                });
            }
        } else {
            this.bgAudio.pause();
            this.isPlaying = false;
            this.updateButtonUI(false);
        }
        return this.isPlaying;
    }

    updateButtonUI(playing) {
        const btn = document.getElementById('audio-toggle-btn');
        const label = document.getElementById('audio-btn-label');
        if (btn) {
            btn.classList.toggle('playing', playing);
        }
        if (label) {
            label.textContent = playing ? 'Играет ♫' : 'Музыка';
        }
    }

    setVolume(vol) {
        this.bgAudio.volume = Math.max(0, Math.min(1, vol));
    }

    playClick() {
        this.init();
        if (this.ctx && this.ctx.state === 'suspended') this.ctx.resume();
        if (!this.ctx) return;

        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(800, now);
        osc.frequency.exponentialRampToValueAtTime(300, now + 0.04);

        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.04);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        osc.stop(now + 0.04);
    }

    playVoteFanfare(faction) {
        this.init();
        if (this.ctx && this.ctx.state === 'suspended') this.ctx.resume();
        if (!this.ctx) return;

        const now = this.ctx.currentTime;
        let notes = [261.63, 329.63, 392.00, 523.25];
        if (faction === 'horde') {
            notes = [174.61, 220.00, 261.63, 349.23];
        } else if (faction === 'the_world') {
            notes = [293.66, 369.99, 440.00, 587.33];
        }

        notes.forEach((freq, i) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = 'triangle';
            osc.frequency.setValueAtTime(freq, now + i * 0.09);

            gain.gain.setValueAtTime(0, now);
            gain.gain.setValueAtTime(0.12, now + i * 0.09);
            gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.09 + 0.45);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now + i * 0.09);
            osc.stop(now + i * 0.09 + 0.5);
        });
    }
}

window.tavernAudio = new AudioManager();

window.toggleMusicPlayback = function(e) {
    if (e) e.preventDefault();
    return window.tavernAudio.toggleMusic();
};

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('audio-toggle-btn');
    if (btn) {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            window.tavernAudio.toggleMusic();
        });
    }
});
