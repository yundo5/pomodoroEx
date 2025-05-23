let isWork = true;
let interval;
let totalRepeats = 1;
let currentRepeat = 0;
let isPaused = false;

function getRadioValue(name) {
    const radios = document.getElementsByName(name);
    for (const radio of radios) {
        if (radio.checked) return radio.value;
    }
    return "";
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
        document.body.style.backgroundColor = isWork ? "#FF6347" : "#4CAF50";

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
                        isWork = !isWork;
                        runTimer(isWork ? durations.work : durations.break);
                    } else {
                        document.getElementById("feedback").classList.remove("hidden");
                    }
                }
            }
        }, 1000);
    }

    runTimer(durations.work);
}

function pausePomodoro() {
    isPaused = !isPaused;
    document.getElementById("pauseBtn").textContent = isPaused ? "Resume" : "Pause";
}

function stopPomodoro() {
    clearInterval(interval);
    resetUI();
}

function resetUI() {
    document.body.style.backgroundColor = "#ffffff";
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
