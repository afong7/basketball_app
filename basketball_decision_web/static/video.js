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



let currentDecisionIndex = 0;
let selectedAnswer = "";
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
        // Pause marker
        const pauseMarker = document.createElement("div");
        pauseMarker.classList.add("decision-marker");

        const pausePercent = (dp.pause_time / video.duration) * 100;
        pauseMarker.style.left = pausePercent + "%";
        markerContainer.appendChild(pauseMarker);

        // Reveal marker
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
  waitingForAnswer = false;
  questionPanel.hidden = true;

  video.play();
}

/* ------------------------------
   Show feedback
--------------------------------*/
function showFeedback(decisionPoint) {
  const wasCorrect = selectedAnswer === decisionPoint.correct_answer;

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

  // Prevent double triggers
  if (waitingForAnswer || waitingForFeedback) return;

  // Player skipped ahead past pause_time → force question
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

  // Pause at decision moment
  if (
    video.currentTime >= currentDecision.pause_time &&
    selectedAnswer === ""
  ) {
    video.pause();
    waitingForAnswer = true;
    showQuestion(currentDecision);
    return;
  }

  // Pause at reveal moment
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

  // ---- SAVE PROGRESS TO SERVER ----
  fetch("/save_progress", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      video_id: window.videoData.videoId,
      correct_answers: correctAnswers,
      total_questions: totalQuestions
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

// let currentDecisionIndex = 0;
// let selectedAnswer = "";
// let correctAnswers = 0;
// let waitingForAnswer = false;
// let waitingForFeedback = false;

// /*
//   Display the question and answer buttons for the current decision point.
// */
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

// /*
//   Save the player's answer, hide the question, and resume the video.
// */
// function selectAnswer(answer) {
//   selectedAnswer = answer;
//   waitingForAnswer = false;
//   questionPanel.hidden = true;

//   video.play();
// }

// /*
//   Show coaching feedback after the video reveals the outcome.
// */
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

// /*
//   Play toward the next decision point after the player has read feedback.
// */
// // continueButton.addEventListener("click", function () {
// //   feedbackPanel.hidden = true;
// //   waitingForFeedback = false;

// //   currentDecisionIndex += 1;
// //   video.play();
// // });
// continueButton.addEventListener("click", function () {
//   feedbackPanel.hidden = true;
//   waitingForFeedback = false;

//   currentDecisionIndex += 1;
//   selectedAnswer = "";

//   video.play();
// });

// /*
//   While the video plays, check whether it has reached a pause or reveal time.
// */
// video.addEventListener("timeupdate", function () {
//   const currentDecision = decisionPoints[currentDecisionIndex];

//   /*
//     There are no more questions once the final decision point is complete.
//   */
//   if (!currentDecision) {
//     return;
//   }

//   /*
//     Pause before the basketball decision and show the question.
//   */
//   if (
//     video.currentTime >= currentDecision.pause_time &&
//     !waitingForAnswer &&
//     !waitingForFeedback &&
//     selectedAnswer === ""
//   ) {
//     video.pause();
//     waitingForAnswer = true;
//     showQuestion(currentDecision);
//     return;
//   }

//   /*
//     Pause after the outcome is visible and show feedback.
//   */
//   if (
//     video.currentTime >= currentDecision.reveal_time &&
//     !waitingForAnswer &&
//     !waitingForFeedback &&
//     selectedAnswer !== ""
//   ) {
//     video.pause();
//     waitingForFeedback = true;
//     showFeedback(currentDecision);
//   }
// });

// /*
//   Reset the saved answer when the video begins playing for the next decision.
// */
// // video.addEventListener("play", function () {
// //   if (!waitingForAnswer && !waitingForFeedback) {
// //     selectedAnswer = "";
// //   }
// // });

// /*
//   Show a simple score when the entire video ends.
// */
// video.addEventListener("ended", function () {
//   const totalQuestions = decisionPoints.length;

//   completionPanel.hidden = false;
//   completionMessage.textContent =
//     "You answered " +
//     correctAnswers +
//     " out of " +
//     totalQuestions +
//     " decisions correctly.";
// });