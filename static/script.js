document.addEventListener("DOMContentLoaded", () => {
    let isWork = true;
    let isPaused = false;
    let isBreak = false;
    let interval;
    let seconds = workMinutes * 60;
    let bgIndex = 1;
    let currentThemeIndex = 0;
    const themes = ["땅", "산", "하늘", "성층권", "우주"];
    const totalImages = 12;
    let currentTheme = themes[currentThemeIndex];
    let backgroundAnimationOff = false;

    const display = document.getElementById("timerDisplay");
    const pauseBtn = document.getElementById("pauseBtn");
    const body = document.getElementById("main-body");
    const bgToggle = document.getElementById("bgToggle");
    const bgMusic = document.getElementById("bgMusic");

    // Flask에서 넘겨주는 BGM 값
    const selectedMusic = "{{ session.get('bgm', 'off') }}";

    bgMusic.loop = true;

    bgToggle.addEventListener("change", () => {
        backgroundAnimationOff = bgToggle.checked;
        applyBackground();
    });

    function updateDisplay() {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        display.textContent = `${m}분 ${s < 10 ? "0" + s : s}초`;
    }

    function preloadAndSetBackground(src) {
        const img = new Image();
        img.onload = () => {
            body.style.backgroundImage = `url('${src}')`;
            body.style.backgroundColor = "";
        };
        img.src = src;
    }

    function applyBackground() {
        if (backgroundAnimationOff) {
            body.style.backgroundImage = "none";
            body.style.backgroundColor = !isPaused && !isBreak ? "green" : "darkred";
        } else {
            changeBackground();
        }
    }

    function changeBackground() {
        if (backgroundAnimationOff) return;

        const path = isPaused || isBreak
            ? `/static/images/나무/${currentTheme}/${currentTheme}-휴식시간.png`
            : `/static/images/나무/${currentTheme}/${currentTheme}-나무${bgIndex}.png`;

        preloadAndSetBackground(path);

        if (!isPaused && !isBreak) {
            bgIndex++;
            if (bgIndex > totalImages) {
                bgIndex = 1;
                currentThemeIndex = (currentThemeIndex + 1) % themes.length;
                currentTheme = themes[currentThemeIndex];
            }
        }
    }

    function startBackgroundRotation() {
        changeBackground();
        setInterval(() => {
            if (!isPaused && !backgroundAnimationOff) {
                changeBackground();
            }
        }, 300000); // 5분 간격
    }

    function playBackgroundMusic() {
        if (selectedMusic && selectedMusic !== "off") {
            bgMusic.src = `/static/music/${selectedMusic}`;
            bgMusic.play().catch((err) => {
                console.log("자동재생 차단:", err);
            });
        }
    }

    function startTimer() {
        updateDisplay();
        playBackgroundMusic();

        interval = setInterval(() => {
            if (!isPaused) {
                if (seconds > 0) {
                    seconds--;
                    updateDisplay();
                } else {
                    if (!isBreak) {
                        isBreak = true;
                        seconds = breakMinutes * 60;
                        applyBackground();
                        updateDisplay();
                    } else {
                        clearInterval(interval);
                        bgMusic.pause();
                        bgMusic.currentTime = 0;
                        window.location.href = "/feedback";
                    }
                }
            }
        }, 1000);
    }

    window.togglePause = function () {
        isPaused = !isPaused;
        pauseBtn.textContent = isPaused ? "▶" : "⏸";
        applyBackground();
        if (isPaused) {
            bgMusic.pause();
        } else {
            bgMusic.play().catch((err) => console.log("재생 오류:", err));
        }
    };

    window.stopTimer = function () {
        clearInterval(interval);
        bgMusic.pause();
        bgMusic.currentTime = 0;
        window.location.href = "/";
    };

    // 초기 실행
    startBackgroundRotation();
    startTimer();
});
