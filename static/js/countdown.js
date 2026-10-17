// Countdown Timer for WoW Forever launch
class WoWCountdown {
    constructor() {
        this.targetDate = null;
        this.timerInterval = null;
        this.prevValues = { days: -1, hours: -1, minutes: -1, seconds: -1 };
    }

    init(targetDateString) {
        this.setTarget(targetDateString);
        this.tick();
        if (this.timerInterval) clearInterval(this.timerInterval);
        this.timerInterval = setInterval(() => this.tick(), 1000);
    }

    setTarget(targetDateString) {
        if (!targetDateString) return;
        this.targetDate = new Date(targetDateString).getTime();
    }

    russianPlural(num, one, two, five) {
        let n = Math.abs(num);
        n %= 100;
        if (n >= 5 && n <= 20) {
            return five;
        }
        n %= 10;
        if (n === 1) {
            return one;
        }
        if (n >= 2 && n <= 4) {
            return two;
        }
        return five;
    }

    padZero(num) {
        return num < 10 ? '0' + num : '' + num;
    }

    tick() {
        if (!this.targetDate) return;
        const now = new Date().getTime();
        const distance = this.targetDate - now;

        const timerBox = document.getElementById('countdown-wrapper');
        const launchedBanner = document.getElementById('server-launched-banner');

        if (distance <= 0) {
            if (timerBox) timerBox.style.display = 'none';
            if (launchedBanner) launchedBanner.style.display = 'block';
            return;
        } else {
            if (timerBox) timerBox.style.display = 'flex';
            if (launchedBanner) launchedBanner.style.display = 'none';
        }

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        this.updateDigit('days', days, this.russianPlural(days, 'День', 'Дня', 'Дней'));
        this.updateDigit('hours', hours, this.russianPlural(hours, 'Час', 'Часа', 'Часов'));
        this.updateDigit('minutes', minutes, this.russianPlural(minutes, 'Минута', 'Минуты', 'Минут'));
        this.updateDigit('seconds', seconds, this.russianPlural(seconds, 'Секунда', 'Секунды', 'Секунд'));
    }

    updateDigit(id, val, label) {
        const numEl = document.getElementById(`cd-${id}-num`);
        const labelEl = document.getElementById(`cd-${id}-label`);

        if (numEl) {
            const formatted = this.padZero(val);
            if (this.prevValues[id] !== val) {
                numEl.textContent = formatted;
                numEl.classList.remove('pulse-tick');
                void numEl.offsetWidth; // trigger reflow
                numEl.classList.add('pulse-tick');
                this.prevValues[id] = val;
            }
        }
        if (labelEl) {
            labelEl.textContent = label;
        }
    }
}

window.wowCountdown = new WoWCountdown();
