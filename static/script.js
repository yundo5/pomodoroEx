let isWork = true;
let interval;
let totalRepeats = 1;
let currentRepeat = 0;
let isPaused = false;

// 배경 애니메이션 관련 요소
const bgVideo = document.getElementById("bgVideo");
const animationToggle = document.getElementById("animationToggle");

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

// 배경 애니메이션 상태 업데이트 함수
function updateAnimationState(on) {
    if (on) {
        bgVideo.removeAttribute("hidden");
        bgVideo.muted = false;
        bgVideo.play();
    } else {
        bgVideo.setAttribute("hidden", true);
        bgVideo.pause();
        bgVideo.currentTime = 0;
    }
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

        // 배경 색상 설정: 애니메이션이 비활성화된 경우에만 적용
        if (!animationToggle.checked) {
            document.body.style.backgroundColor = isWork ? "#FF6347" : "#4CAF50";
        } else {
            document.body.style.backgroundColor = "transparent";
        }

        clearInterval(interval);
        interval = setInterval(() => {
            if (!isPaused) {
                timeLeft--;
                updateTimerDisplay(timeLeft);
                if (timeLeft <= 0) {
                    clearInterval(interval);

                    if (isWork && document.getElementById("alarmToggle").checked) {
                        document.getElementById("alarmSound").play();
                    }

                    if (!isWork) currentRepeat++;
                    if (currentRepeat < totalRepeats) {
                        // 작업 세션 종료 후 애니메이션 정지
                        if (isWork && animationToggle.checked) {
                            updateAnimationState(false);
                        }

                        isWork = !isWork;
                        runTimer(isWork ? durations.work : durations.break);
                    } else {
                        updateAnimationState(false);  // 모든 세션 종료 시
                        stopBackgroundMusic();        // 배경 음악 정지
                        document.getElementById("feedback").classList.remove("hidden");
                    }
                }
            }
        }, 1000);
    }

    runTimer(durations.work);

    if (animationToggle.checked) {
        updateAnimationState(true);  // 배경 애니메이션 시작
    }

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
    clearInterval(interval); // 타이머 중지
    updateAnimationState(false); // 배경 애니메이션 정지
    stopBackgroundMusic(); // 배경 음악 정지
    resetUI(); // UI 초기화
}

// UI 초기화 함수
function resetUI() {
    // 배경 애니메이션 여부에 따른 배경 색상 설정
    document.body.style.backgroundColor = animationToggle.checked ? "transparent" : "#ffffff";
    showSettings(); // 설정 화면 표시
    updateTimerDisplay(0); // 타이머 표시 초기화
    isPaused = false; // 일시정지 상태 초기화
}

// 타이머 표시 업데이트 함수
function updateTimerDisplay(seconds) {
    const m = String(Math.floor(seconds / 60)).padStart(2, "0");
    const s = String(seconds % 60).padStart(2, "0");
    document.getElementById("timer").textContent = `${m}:${s}`;
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

