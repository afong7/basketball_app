const video = document.getElementById("training-video");
const questionPanel = document.getElementById("question-panel");
const questionText = document.getElementById("question-text");
const answerChoices = document.getElementById("answer-choices");

const feedbackPanel = document.getElementById("feedback-panel");
const feedbackHeading = document.getElementById("feedback-heading");
const feedbackMessage = document.getElementById("feedback-message");
const continueButton = document.getElementById("continue-button");

const completionPanel = document.getElementById("completion-panel");
const completionMessage = document.getElementById("completion-message");

const decisionPoints = window.videoData.decisionPoints;
const decisionCounter = document.getElementById("decision-counter");
const markerContainer = document.getElementById("decision-markers");
const progressBar = document.getElementById("progress-bar");

// ⭐ NEW ANALYTICS VARIABLES ⭐
let currentDecisionIndex = 0;
let selectedAnswer = "";
let chosenAnswer = "";          // NEW
let isCorrect = false;          // NEW
let questionStartTime = 0;      // NEW
let timeTaken = 0;              // NEW
let attemptNumber = 1;          // NEW
const video_id = window.videoData.videoId;   // NEW

let correctAnswers = 0;
let waitingForAnswer = false;
let waitingForFeedback = false;

/* ------------------------------
   Progress bars
--------------------------------*/
function updateDecisionCounter() {
    decisionCounter.hidden = false;
    decisionCounter.textContent =
        "Decision " + (currentDecisionIndex + 1) + " of " + decisionPoints.length;
}

video.addEventListener("timeupdate", function () {
    const percent = (video.currentTime / video.duration) * 100;
    progressBar.style.width = percent + "%";
});

function createDecisionMarkers() {
    decisionPoints.forEach(dp => {
        const pauseMarker = document.createElement("div");
        pauseMarker.classList.add("decision-marker");

        const pausePercent = (dp.pause_time / video.duration) * 100;
        pauseMarker.style.left = pausePercent + "%";
        markerContainer.appendChild(pauseMarker);

        const revealMarker = document.createElement("div");
        revealMarker.classList.add("reveal-marker");

        const revealPercent = (dp.reveal_time / video.duration) * 100;
        revealMarker.style.left = revealPercent + "%";
        markerContainer.appendChild(revealMarker);
    });
}

video.addEventListener("loadedmetadata", createDecisionMarkers);

/* ------------------------------
   Show Question
--------------------------------*/
function showQuestion(decisionPoint) {
    questionStartTime = Date.now();   // ⭐ NEW

    questionText.textContent = decisionPoint.question;
    answerChoices.innerHTML = "";

    decisionPoint.choices.forEach(function (choice) {
        const answerButton = document.createElement("button");
        answerButton.type = "button";
        answerButton.textContent = choice;

        answerButton.addEventListener("click", function () {
            selectAnswer(choice);
        });

        answerChoices.appendChild(answerButton);
    });

    questionPanel.hidden = false;
}

/* ------------------------------
   Player selects an answer
--------------------------------*/
function selectAnswer(answer) {
    selectedAnswer = answer;
    chosenAnswer = answer;   // ⭐ NEW

    waitingForAnswer = false;
    questionPanel.hidden = true;

    video.play();
}

/* ------------------------------
   Show feedback
--------------------------------*/
function showFeedback(decisionPoint) {
    timeTaken = Date.now() - questionStartTime;   // ⭐ NEW
    isCorrect = (selectedAnswer === decisionPoint.correct_answer); // ⭐ NEW

    const wasCorrect = isCorrect;

    if (wasCorrect) {
        correctAnswers += 1;
        feedbackHeading.textContent = "Correct!";
    } else {
        feedbackHeading.textContent = "Not quite.";
    }

    feedbackMessage.textContent = decisionPoint.explanation;
    feedbackPanel.hidden = false;
}

/* ------------------------------
   Continue after feedback
--------------------------------*/
continueButton.addEventListener("click", function () {
    feedbackPanel.hidden = true;
    waitingForFeedback = false;

    currentDecisionIndex += 1;
    selectedAnswer = "";

    video.play();
});

/* ------------------------------
   Main video loop
--------------------------------*/
video.addEventListener("timeupdate", function () {
    const currentDecision = decisionPoints[currentDecisionIndex];
    if (!currentDecision) return;

    if (waitingForAnswer || waitingForFeedback) return;

    if (
        video.currentTime > currentDecision.pause_time &&
        selectedAnswer === ""
    ) {
        video.pause();
        waitingForAnswer = true;
        showQuestion(currentDecision);
        updateDecisionCounter();
        return;
    }

    if (
        video.currentTime >= currentDecision.pause_time &&
        selectedAnswer === ""
    ) {
        video.pause();
        waitingForAnswer = true;
        showQuestion(currentDecision);
        return;
    }

    if (
        selectedAnswer !== "" &&
        video.currentTime >= currentDecision.reveal_time
    ) {
        video.pause();
        waitingForFeedback = true;
        showFeedback(currentDecision);
        return;
    }
});

/* ------------------------------
   Completion screen
--------------------------------*/
video.addEventListener("ended", function () {
    const totalQuestions = decisionPoints.length;

    completionPanel.hidden = false;
    completionMessage.textContent =
        "You answered " +
        correctAnswers +
        " out of " +
        totalQuestions +
        " decisions correctly.";

    // ⭐ PREP ANALYTICS VALUES ⭐
    const correct = correctAnswers;
    const total = decisionPoints.length;
    attemptNumber += 1;

    // ---- SAVE PROGRESS TO SERVER ----
    fetch("/save_progress", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            video_id: video_id,
            correct_answers: correct,
            total_questions: total,

            selected_answer: chosenAnswer,
            is_correct: isCorrect,
            decision_point_index: currentDecisionIndex,
            time_taken: timeTaken,
            attempt_number: attemptNumber
        })
    });
});



// const video = document.getElementById("training-video");
// const questionPanel = document.getElementById("question-panel");
// const questionText = document.getElementById("question-text");
// const answerChoices = document.getElementById("answer-choices");

// const feedbackPanel = document.getElementById("feedback-panel");
// const feedbackHeading = document.getElementById("feedback-heading");
// const feedbackMessage = document.getElementById("feedback-message");
// const continueButton = document.getElementById("continue-button");

// const completionPanel = document.getElementById("completion-panel");
// const completionMessage = document.getElementById("completion-message");

// const decisionPoints = window.videoData.decisionPoints;
// const decisionCounter = document.getElementById("decision-counter");
// const markerContainer = document.getElementById("decision-markers");
// const progressBar = document.getElementById("progress-bar");



// let currentDecisionIndex = 0;
// let selectedAnswer = "";
// let correctAnswers = 0;
// let waitingForAnswer = false;
// let waitingForFeedback = false;

// /* ------------------------------
//    Progress bars
// --------------------------------*/
// function updateDecisionCounter() {
//     decisionCounter.hidden = false;
//     decisionCounter.textContent =
//         "Decision " + (currentDecisionIndex + 1) + " of " + decisionPoints.length;
// }

// video.addEventListener("timeupdate", function () {
//     const percent = (video.currentTime / video.duration) * 100;
//     progressBar.style.width = percent + "%";
// });

// function createDecisionMarkers() {
//     decisionPoints.forEach(dp => {
//         // Pause marker
//         const pauseMarker = document.createElement("div");
//         pauseMarker.classList.add("decision-marker");

//         const pausePercent = (dp.pause_time / video.duration) * 100;
//         pauseMarker.style.left = pausePercent + "%";
//         markerContainer.appendChild(pauseMarker);

//         // Reveal marker
//         const revealMarker = document.createElement("div");
//         revealMarker.classList.add("reveal-marker");

//         const revealPercent = (dp.reveal_time / video.duration) * 100;
//         revealMarker.style.left = revealPercent + "%";
//         markerContainer.appendChild(revealMarker);
//     });
// }

// video.addEventListener("loadedmetadata", createDecisionMarkers);

// /* ------------------------------
//    Show Question
// --------------------------------*/
// function showQuestion(decisionPoint) {
//   questionText.textContent = decisionPoint.question;
//   answerChoices.innerHTML = "";

//   decisionPoint.choices.forEach(function (choice) {
//     const answerButton = document.createElement("button");
//     answerButton.type = "button";
//     answerButton.textContent = choice;

//     answerButton.addEventListener("click", function () {
//       selectAnswer(choice);
//     });

//     answerChoices.appendChild(answerButton);
//   });

//   questionPanel.hidden = false;
// }

// /* ------------------------------
//    Player selects an answer
// --------------------------------*/
// function selectAnswer(answer) {
//   selectedAnswer = answer;
//   waitingForAnswer = false;
//   questionPanel.hidden = true;

//   video.play();
// }

// /* ------------------------------
//    Show feedback
// --------------------------------*/
// function showFeedback(decisionPoint) {
//   const wasCorrect = selectedAnswer === decisionPoint.correct_answer;

//   if (wasCorrect) {
//     correctAnswers += 1;
//     feedbackHeading.textContent = "Correct!";
//   } else {
//     feedbackHeading.textContent = "Not quite.";
//   }

//   feedbackMessage.textContent = decisionPoint.explanation;
//   feedbackPanel.hidden = false;
// }

// /* ------------------------------
//    Continue after feedback
// --------------------------------*/
// continueButton.addEventListener("click", function () {
//   feedbackPanel.hidden = true;
//   waitingForFeedback = false;

//   currentDecisionIndex += 1;
//   selectedAnswer = "";

//   video.play();
// });

// /* ------------------------------
//    Main video loop
// --------------------------------*/
// video.addEventListener("timeupdate", function () {
//   const currentDecision = decisionPoints[currentDecisionIndex];
//   if (!currentDecision) return;

//   // Prevent double triggers
//   if (waitingForAnswer || waitingForFeedback) return;

//   // Player skipped ahead past pause_time → force question
//   if (
//     video.currentTime > currentDecision.pause_time &&
//     selectedAnswer === ""
//   ) {
//     video.pause();
//     waitingForAnswer = true;
//     showQuestion(currentDecision);
//     updateDecisionCounter();

//     return;
//   }

//   // Pause at decision moment
//   if (
//     video.currentTime >= currentDecision.pause_time &&
//     selectedAnswer === ""
//   ) {
//     video.pause();
//     waitingForAnswer = true;
//     showQuestion(currentDecision);
//     return;
//   }

//   // Pause at reveal moment
//   if (
//     selectedAnswer !== "" &&
//     video.currentTime >= currentDecision.reveal_time
//   ) {
//     video.pause();
//     waitingForFeedback = true;
//     showFeedback(currentDecision);
//     return;
//   }
// });

// /* ------------------------------
//    Completion screen
// --------------------------------*/
// video.addEventListener("ended", function () {
//   const totalQuestions = decisionPoints.length;

//   completionPanel.hidden = false;
//   completionMessage.textContent =
//     "You answered " +
//     correctAnswers +
//     " out of " +
//     totalQuestions +
//     " decisions correctly.";

//   // ---- SAVE PROGRESS TO SERVER ----
//   fetch("/save_progress", {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json"
//     },
//     body: JSON.stringify({
//       video_id: video_id,
//       correct_answers: correct,
//       total_questions: total,
//       selected_answer: chosenAnswer,
//       is_correct: isCorrect,
//       decision_point_index: currentDecisionIndex,
//       time_taken: timeTaken, 
//       attempt_number: attemptNumber
//     })
//   });
// });