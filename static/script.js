document.addEventListener("DOMContentLoaded", () => {
    let isWork = true;
    let interval;
    let totalRepeats = 1;
    let currentRepeat = 0;
    let isPaused = false;

    const progressImage = document.getElementById("progressImage");
    const bgMusic = document.getElementById("bgMusic");
    bgMusic.loop = true;
    let selectedMusic = "";

    // ✅ 음악 버튼 존재 시에만 이벤트 바인딩 (안전)
    const musicOceanBtn = document.getElementById("musicOcean");
    if (musicOceanBtn) musicOceanBtn.addEventListener("click", () => selectMusic("ocean.mp3"));
    const musicHeaterBtn = document.getElementById("musicHeater");
    if (musicHeaterBtn) musicHeaterBtn.addEventListener("click", () => selectMusic("heater.mp3"));
    const musicRainBtn = document.getElementById("musicRain");
    if (musicRainBtn) musicRainBtn.addEventListener("click", () => selectMusic("rain.mp3"));

    function getRadioValue(name) {
        const radios = document.getElementsByName(name);
        for (const radio of radios) {
            if (radio.checked) return radio.value;
        }
        return "";
    }

    function playBackgroundMusic() {
        if (selectedMusic) {
            bgMusic.src = `/static/music/${selectedMusic}`;
            bgMusic.play().catch((error) => {
                console.log("음악 재생 오류:", error);
            });
        }
    }

    function stopBackgroundMusic() {
        bgMusic.pause();
        bgMusic.currentTime = 0;
    }

    function selectMusic(musicFile) {
        selectedMusic = musicFile;
    }

    // ✅ 전역 함수 등록
    window.startPomodoro = function () {
        const workMinutes = parseInt(document.getElementById("workMinutes").value) || 25;
        const breakMinutes = parseInt(document.getElementById("breakMinutes").value) || 5;
        totalRepeats = parseInt(document.getElementById("repeatCount").value) || 1;

        const focus = getRadioValue("focus");
        const flow = getRadioValue("flow");
        const task = getRadioValue("task");

        hideSettings();
        isWork = true;
        currentRepeat = 0;

        const durations = {
            work: workMinutes * 60,
            break: breakMinutes * 60
        };

        function runTimer(duration) {
            let timeLeft = duration;
            updateTimerDisplay(timeLeft);
            updateProgressImage(0, duration);

            clearInterval(interval);
            interval = setInterval(() => {
                if (!isPaused) {
                    timeLeft--;
                    updateTimerDisplay(timeLeft);
                    updateProgressImage(duration - timeLeft, duration);

                    if (timeLeft <= 0) {
                        clearInterval(interval);
                        if (isWork && document.getElementById("alarmToggle").checked) {
                            document.getElementById("alarmSound").play();
                        }

                        if (!isWork) currentRepeat++;
                        if (currentRepeat < totalRepeats) {
                            isWork = !isWork;
                            runTimer(isWork ? durations.work : durations.break);
                        } else {
                            stopBackgroundMusic();
                            document.getElementById("feedback").classList.remove("hidden");
                        }
                    }
                }
            }, 1000);
        }

        runTimer(durations.work);
        playBackgroundMusic();
    }

    window.pausePomodoro = function () {
        isPaused = !isPaused;
        document.getElementById("pauseBtn").textContent = isPaused ? "재개" : "일시정지";
        if (isPaused) {
            bgMusic.pause();
        } else {
            bgMusic.play();
        }
    }

    window.stopPomodoro = function () {
        clearInterval(interval);
        stopBackgroundMusic();
        resetUI();
    }

    function resetUI() {
        document.body.style.backgroundColor = "#ffffff";
        showSettings();
        updateTimerDisplay(0);
        isPaused = false;
        if (progressImage) progressImage.src = "/static/images/image1.png";
    }

    function updateTimerDisplay(seconds) {
        const m = String(Math.floor(seconds / 60)).padStart(2, "0");
        const s = String(seconds % 60).padStart(2, "0");
        document.getElementById("timer").textContent = `${m}:${s}`;
    }

    function updateProgressImage(elapsed, total) {
        if (!progressImage) return;
        const percent = (elapsed / total) * 100;
        const index = Math.min(7, Math.floor(percent / 12.5));
        progressImage.src = `/static/images/image${index + 1}.png`;
    }

    function hideSettings() {
        const settings = document.getElementById("settings");
        if (settings) settings.classList.add("hidden");
        document.getElementById("pauseBtn").classList.remove("hidden");
        document.getElementById("stopBtn").classList.remove("hidden");
    }

    function showSettings() {
        const settings = document.getElementById("settings");
        if (settings) settings.classList.remove("hidden");
        document.getElementById("pauseBtn").classList.add("hidden");
        document.getElementById("stopBtn").classList.add("hidden");
        document.getElementById("pauseBtn").textContent = "일시정지";
    }

    window.submitFeedback = function () {
        const focusFeedback = getRadioValue("focusFeedback");
        const breakFeedback = getRadioValue("breakFeedback");

        const focus = getRadioValue("focus");
        const flow = getRadioValue("flow");
        const task = getRadioValue("task");

        fetch("/submit_feedback", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                timestamp: new Date().toISOString(),
                focus,
                flow,
                task,
                focusFeedback,
                breakFeedback
            })
        }).then(() => {
            alert("피드백이 제출되었습니다. 감사합니다!");
            showSettings();
            document.getElementById("feedback").classList.add("hidden");
        });
    }
});