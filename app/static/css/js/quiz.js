let currentQuestions = [];
const selectedAnswers = {};

const quizContainer = document.getElementById("quizContainer");
const resultBox = document.getElementById("quizResult");
const categorySelect = document.getElementById("categorySelect");
const submitBtn = document.getElementById("submitQuizBtn");

async function loadQuestions(weekly = false) {
  const category = categorySelect.value;
  const params = new URLSearchParams({ limit: 5 });
  if (category) params.set("category", category);
  if (weekly) params.set("weekly", "true");

  Object.keys(selectedAnswers).forEach((key) => delete selectedAnswers[key]);
  resultBox.innerHTML = "";
  quizContainer.innerHTML = "<p class='text-muted'>Loading questions...</p>";

  const response = await fetch(`/quiz/api/questions?${params.toString()}`);
  currentQuestions = await response.json();
  renderQuestions(weekly);
}

function renderQuestions(weekly) {
  quizContainer.innerHTML = "";

  if (currentQuestions.length === 0) {
    quizContainer.innerHTML = "<p class='text-muted'>No reviewed questions are available yet for this filter.</p>";
    submitBtn.disabled = true;
    return;
  }

  submitBtn.disabled = false;

  currentQuestions.forEach((q, index) => {
    const div = document.createElement("div");
    div.className = "border-bottom pb-3 mb-3";
    div.innerHTML = `<p><strong>${index + 1}. ${q.question}</strong> <span class="badge bg-light text-dark">${q.category}</span></p>`;

    q.options.forEach((option) => {
      const label = document.createElement("label");
      label.className = "option";
      label.innerHTML = `<input type="radio" name="q-${q.id}" value="${option}"> ${option}`;
      label.querySelector("input").addEventListener("change", (e) => {
        selectedAnswers[q.id] = e.target.value;
      });
      div.appendChild(label);
    });

    quizContainer.appendChild(div);
  });

  quizContainer.dataset.weekly = weekly ? "true" : "false";
}

submitBtn.addEventListener("click", async () => {
  if (Object.keys(selectedAnswers).length === 0) {
    resultBox.innerHTML = "<div class='alert alert-warning'>Please answer at least one question.</div>";
    return;
  }

  const isWeekly = quizContainer.dataset.weekly === "true";

  const response = await fetch("/quiz/api/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      answers: selectedAnswers,
      category: categorySelect.value || "mixed",
      is_weekly: isWeekly,
    }),
  });

  const data = await response.json();

  if (data.error) {
    resultBox.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
    return;
  }

  let breakdown = "";
  data.results.forEach((r) => {
    const q = currentQuestions.find((item) => item.id === r.question_id);
    breakdown += `
      <div class="card bg-light p-3 mb-2">
        <strong>${q ? q.question : "Question"}</strong>
        <p class="${r.correct ? "text-success" : "text-danger"} mb-1">
          ${r.correct ? "Correct" : `Incorrect. Correct answer: ${r.correct_answer}`}
        </p>
        <small>${r.explanation}</small>
      </div>`;
  });

  resultBox.innerHTML = `
    <div class="alert alert-success">
      You scored ${data.score}/${data.total} and earned ${data.points} points.
    </div>
    ${breakdown}`;

  submitBtn.disabled = true;
});

document.getElementById("weeklyBtn").addEventListener("click", () => loadQuestions(true));
categorySelect.addEventListener("change", () => loadQuestions(false));

loadQuestions(false);
