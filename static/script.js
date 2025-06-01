let isWork = true;
let interval;
let totalRepeats = 1;
let currentRepeat = 0;
let isPaused = false;

// 배경 이미지 관련 요소
const progressImage = document.getElementById("progressImage");

// 배경 음악 관련 요소
const bgMusic = document.getElementById("bgMusic");
bgMusic.loop = true;
let selectedMusic = "";

// 음악 선택 버튼 이벤트 리스너
document.getElementById("musicOcean").addEventListener("click", () => selectMusic("ocean.mp3"));
document.getElementById("musicHeater").addEventListener("click", () => selectMusic("heater.mp3"));
document.getElementById("musicRain").addEventListener("click", () => selectMusic("rain.mp3"));

function getRadioValue(name) {
    const radios = document.getElementsByName(name);
    for (const radio of radios) {
        if (radio.checked) return radio.value;
    }
    return "";
}

// 배경 음악 재생 함수
function playBackgroundMusic() {
    if (selectedMusic) {
        bgMusic.src = `/static/music/${selectedMusic}`;
        bgMusic.play().catch((error) => {
            console.log("음악 재생 오류:", error);
        });
    }
}

// 배경 음악 정지 함수
function stopBackgroundMusic() {
    bgMusic.pause();
    bgMusic.currentTime = 0;
}

// 배경 음악 선택 함수
function selectMusic(musicFile) {
    selectedMusic = musicFile;
    // 음악은 startPomodoro에서 재생됩니다.
}

function startPomodoro() {
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
        updateProgressImage(0, duration);  // 초기 이미지 설정

        document.body.style.backgroundColor = isWork ? "#FF6347" : "#4CAF50";

        clearInterval(interval);
        interval = setInterval(() => {
            if (!isPaused) {
                timeLeft--;
                updateTimerDisplay(timeLeft);
                updateProgressImage(duration - timeLeft, duration);  // 이미지 갱신

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
    playBackgroundMusic(); // 배경 음악 재생
}

function pausePomodoro() {
    isPaused = !isPaused;
    document.getElementById("pauseBtn").textContent = isPaused ? "재개" : "일시정지";
    if (isPaused) {
        bgMusic.pause();
    } else {
        bgMusic.play();
    }
}

// Pomodoro 타이머 중지 함수
function stopPomodoro() {
    clearInterval(interval);
    stopBackgroundMusic();
    resetUI();
}

// UI 초기화 함수
function resetUI() {
    document.body.style.backgroundColor = "#ffffff";
    showSettings();
    updateTimerDisplay(0);
    isPaused = false;
    if (progressImage) progressImage.src = "/static/images/image1.jpg";  // 초기 이미지 복원
}

// 타이머 표시 업데이트 함수
function updateTimerDisplay(seconds) {
    const m = String(Math.floor(seconds / 60)).padStart(2, "0");
    const s = String(seconds % 60).padStart(2, "0");
    document.getElementById("timer").textContent = `${m}:${s}`;
}

// 이미지 교체 함수
function updateProgressImage(elapsed, total) {
    if (!progressImage) return;
    const percent = (elapsed / total) * 100;
    const index = Math.min(7, Math.floor(percent / 12.5));
    progressImage.src = `/static/images/image${index + 1}.png`;
}

// 설정 화면 숨기기 함수
function hideSettings() {
    document.getElementById("settings").classList.add("hidden");
    document.getElementById("pauseBtn").classList.remove("hidden");
    document.getElementById("stopBtn").classList.remove("hidden");
}

// 설정 화면 표시 함수
function showSettings() {
    document.getElementById("settings").classList.remove("hidden");
    document.getElementById("pauseBtn").classList.add("hidden");
    document.getElementById("stopBtn").classList.add("hidden");
    document.getElementById("pauseBtn").textContent = "일시정지";
}

// 피드백 제출 함수
function submitFeedback() {
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
