let isWork = true;
let interval;
let totalRepeats = 1;
let currentRepeat = 0;
let isPaused = false;

// ✅ 애니메이션 관련 요소 참조
const bgVideo = document.getElementById("bgVideo");
const animationToggle = document.getElementById("animationToggle");

function getRadioValue(name) {
    const radios = document.getElementsByName(name);
    for (const radio of radios) {
        if (radio.checked) return radio.value;
    }
    return "";
}

// ✅ 애니메이션 상태 제어 함수
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

        // ✅ 배경색: 애니메이션이 꺼져 있을 때만 적용
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
                        // ✅ 집중 → 휴식 전환이면 애니메이션 끄기
                        if (isWork && animationToggle.checked) {
                            updateAnimationState(false);
                        }

                        isWork = !isWork;
                        runTimer(isWork ? durations.work : durations.break);
                    } else {
                        updateAnimationState(false);  // 마지막 반복 종료 시
                        document.getElementById("feedback").classList.remove("hidden");
                    }
                }
            }
        }, 1000);
    }

    runTimer(durations.work);

    if (animationToggle.checked) {
        updateAnimationState(true);  // ✅ 애니메이션 시작
    }
}

function pausePomodoro() {
    isPaused = !isPaused;
    document.getElementById("pauseBtn").textContent = isPaused ? "Resume" : "Pause";
}

function stopPomodoro() {
    clearInterval(interval);
    updateAnimationState(false);
    resetUI();
}

function resetUI() {
    // ✅ 애니메이션 여부에 따라 배경 리셋
    document.body.style.backgroundColor = animationToggle.checked ? "transparent" : "#ffffff";
    showSettings();
    updateTimerDisplay(0);
    isPaused = false;
}

function updateTimerDisplay(seconds) {
    const m = String(Math.floor(seconds / 60)).padStart(2, "0");
    const s = String(seconds % 60).padStart(2, "0");
    document.getElementById("timer").textContent = `${m}:${s}`;
}

function hideSettings() {
    document.getElementById("settings").classList.add("hidden");
    document.getElementById("pauseBtn").classList.remove("hidden");
    document.getElementById("stopBtn").classList.remove("hidden");
}

function showSettings() {
    document.getElementById("settings").classList.remove("hidden");
    document.getElementById("pauseBtn").classList.add("hidden");
    document.getElementById("stopBtn").classList.add("hidden");
    document.getElementById("pauseBtn").textContent = "Pause";
}

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
        alert("Feedback submitted. Thank you!");
        showSettings();
        document.getElementById("feedback").classList.add("hidden");
    });
}
