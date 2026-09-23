const scenarioPlayer = document.getElementById("scenarioPlayer");
const scenarioTitle = document.getElementById("scenarioTitle");
const scenarioText = document.getElementById("scenarioText");
const scenarioChoices = document.getElementById("scenarioChoices");
const scenarioFeedback = document.getElementById("scenarioFeedback");

let activeScenarioId = null;

async function startScenario(scenarioId) {
  activeScenarioId = scenarioId;
  const response = await fetch(`/scenarios/api/${scenarioId}/start`);
  const data = await response.json();

  scenarioPlayer.classList.remove("d-none");
  scenarioFeedback.classList.add("d-none");
  scenarioTitle.textContent = data.title;
  renderNode(data);
  scenarioPlayer.scrollIntoView({ behavior: "smooth" });
}

function renderNode(data) {
  scenarioText.textContent = data.text;
  scenarioChoices.innerHTML = "";

  if (data.is_end || data.choices.length === 0) {
    scenarioChoices.innerHTML = "<div class='alert alert-info'>Scenario complete. Choose another scenario above to keep learning.</div>";
    return;
  }

  data.choices.forEach((choice) => {
    const btn = document.createElement("button");
    btn.className = "btn btn-outline-primary text-start";
    btn.textContent = choice.text;
    btn.addEventListener("click", () => chooseOption(data.node_id, choice.id));
    scenarioChoices.appendChild(btn);
  });
}

async function chooseOption(nodeId, choiceId) {
  const response = await fetch(`/scenarios/api/${activeScenarioId}/choose`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ node_id: nodeId, choice_id: choiceId }),
  });

  const data = await response.json();

  scenarioFeedback.classList.remove("d-none");
  scenarioFeedback.textContent = `${data.feedback} (+${data.points} points)`;

  renderNode(data);
}

document.querySelectorAll(".scenario-choice").forEach((card) => {
  card.addEventListener("click", () => startScenario(card.dataset.scenarioId));
});
