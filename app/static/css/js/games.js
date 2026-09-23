// ---------------- Tabs ----------------
document.querySelectorAll("#gameTabs .nav-link").forEach((tabBtn) => {
  tabBtn.addEventListener("click", () => {
    document.querySelectorAll("#gameTabs .nav-link").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".game-panel").forEach((p) => p.classList.add("d-none"));
    tabBtn.classList.add("active");
    document.getElementById(`panel-${tabBtn.dataset.tab}`).classList.remove("d-none");
  });
});

// ---------------- Snakes & Ladders ----------------
const slPiece = document.getElementById("slPiece");
const slResult = document.getElementById("slResult");
const slQuestion = document.getElementById("slQuestion");
const slTurn = document.getElementById("slTurn");
const slBoard = document.getElementById("slBoard");
const slRoomCode = document.getElementById("slRoomCode");
const slRoomInfo = document.getElementById("slRoomInfo");
const slStartBtn = document.getElementById("slStartBtn");
const slRestartBtn = document.getElementById("slRestartBtn");
let currentSlQuestion = null;
let roomCode = localStorage.getItem("rq_snake_room") || "";
let pollingTimer = null;

const snakes = {17:7,54:34,62:19,87:49,98:79};
const ladders = {3:22,8:30,28:55,40:70,50:69,63:81};

function buildBoard(players = []) {
  slBoard.innerHTML = "";
  const byPos = {};
  players.forEach((p, i) => { (byPos[p.position] ||= []).push({p, i}); });
  for (let pos = 1; pos <= 100; pos++) {
    const cell = document.createElement("div");
    cell.className = "sl-cell";
    cell.dataset.position = pos;
    const row = Math.floor((pos - 1) / 10);
    const col = row % 2 === 0 ? (pos - 1) % 10 : 9 - ((pos - 1) % 10);
    cell.style.gridColumn = String(col + 1);
    cell.style.gridRow = String(10 - row);
    cell.innerHTML = `<span>${pos}</span>`;
    if (snakes[pos]) cell.innerHTML += `<span class="snake">🐍</span>`;
    if (ladders[pos]) cell.innerHTML += `<span class="ladder">🪜</span>`;
    (byPos[pos] || []).forEach(({p, i}) => {
      const marker = document.createElement("span");
      marker.className = "marker";
      marker.title = p.name;
      marker.textContent = String(i + 1);
      marker.style.background = ["#e74c3c", "#3498db", "#27ae60", "#8e44ad"][i % 4];
      cell.appendChild(marker);
    });
    slBoard.appendChild(cell);
  }
}

function renderRoom(state) {
  if (!state) return;
  buildBoard(state.players || []);
  const me = (state.players || []).find(p => p.name === window.RQ_USER_NAME);
  if (me) slPiece.textContent = me.position;
  const current = state.players?.[state.turn_index];
  const winner = (state.players || []).find(p => p.position === 100);
  slTurn.innerHTML = winner
    ? `🏆 <strong>${winner.name}</strong> reached square 100! Hit Restart to play again.`
    : state.started
    ? `<strong>${current?.name || "Player"}</strong>'s turn${current?.name === window.RQ_USER_NAME ? " — answer the question!" : " — waiting..."}`
    : (state.players?.length >= 2 ? "Ready to restart or waiting to start." : "Waiting for another player...");
  slStartBtn.disabled = !(state.players?.length >= 2 && !state.started);
  slRestartBtn.disabled = !state.code;
  slRoomInfo.innerHTML = `<strong>Room:</strong> <code>${state.code}</code><br><strong>Players:</strong> ${state.players.map(p => `${p.name} (${p.position})`).join(", ")}`;
}

async function roomRequest(url, options = {}) {
  const response = await fetch(url, options);
  return response.json();
}

async function createRoom() {
  const data = await roomRequest("/games/api/snakes-ladders/multiplayer/create", {method:"POST", headers:{"Content-Type":"application/json"}});
  if (data.error) return showSlError(data.error);
  roomCode = data.code; localStorage.setItem("rq_snake_room", roomCode); slRoomCode.value = roomCode; renderRoom(data); startPolling();
}

async function joinRoom() {
  const code = slRoomCode.value.trim().toUpperCase();
  if (!code) return showSlError("Enter a room code.");
  const data = await roomRequest("/games/api/snakes-ladders/multiplayer/join", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({code})});
  if (data.error) return showSlError(data.error);
  roomCode = code; localStorage.setItem("rq_snake_room", roomCode); renderRoom(data); startPolling();
}

async function startRoom() {
  if (!roomCode) return showSlError("Create or join a room first.");
  const data = await roomRequest("/games/api/snakes-ladders/multiplayer/start", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({code:roomCode})});
  if (data.error) return showSlError(data.error);
  renderRoom(data); loadMultiplayerQuestion();
}

async function pollRoom() {
  if (!roomCode) return;
  const data = await roomRequest(`/games/api/snakes-ladders/multiplayer/state/${roomCode}`);
  if (!data.error) { renderRoom(data); if (data.started && !currentSlQuestion) loadMultiplayerQuestion(); }
}
function startPolling() { clearInterval(pollingTimer); pollingTimer = setInterval(pollRoom, 1500); }
function showSlError(message) { slResult.innerHTML = `<div class="alert alert-danger">${message}</div>`; }

async function loadMultiplayerQuestion() {
  if (!roomCode) return;
  const data = await roomRequest(`/games/api/snakes-ladders/multiplayer/question/${roomCode}`);
  if (data.waiting) { slQuestion.innerHTML = `<div class="alert alert-secondary">Waiting for <strong>${data.turn}</strong>...</div>`; return; }
  if (data.error) { slQuestion.innerHTML = `<div class="alert alert-warning">${data.error}</div>`; return; }
  currentSlQuestion = data;
  slQuestion.innerHTML = `<p><strong>${data.question}</strong></p><div>${data.options.map(o => `<button class="btn btn-outline-primary btn-sm me-2 mb-2 sl-option-btn" data-answer="${o}">${o}</button>`).join("")}</div>`;
  document.querySelectorAll(".sl-option-btn").forEach(btn => btn.addEventListener("click", () => answerMultiplayer(btn.dataset.answer)));
}

async function answerMultiplayer(answer) {
  if (!currentSlQuestion || !roomCode) return;
  document.querySelectorAll(".sl-option-btn").forEach(b => b.disabled = true);
  const data = await roomRequest(`/games/api/snakes-ladders/multiplayer/answer/${roomCode}`, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({question_id:currentSlQuestion.id, answer})});
  if (data.error) return showSlError(data.error);
  renderRoom(data.state);
  if (!data.correct) {
    slResult.innerHTML = `<div class="alert alert-warning">Incorrect. Your turn is lost.<br><small>${data.explanation || ""}</small></div>`;
  } else {
    const eventText = data.event === "ladder" ? "🪜 Ladder!" : data.event === "snake" ? "🐍 Snake!" : "";
    slResult.innerHTML = `<div class="alert alert-success">${data.player_name} rolled <strong>${data.dice}</strong>. ${eventText}<br>${data.lesson}</div>`;
  }
  currentSlQuestion = null;
  setTimeout(loadMultiplayerQuestion, 700);
}

async function restartRoom() {
  if (!roomCode) return showSlError("Create or join a room first.");
  slResult.innerHTML = "";
  slQuestion.innerHTML = "";
  currentSlQuestion = null;
  const data = await roomRequest("/games/api/snakes-ladders/multiplayer/restart", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({code:roomCode})});
  if (data.error) return showSlError(data.error);
  renderRoom(data);
}

document.getElementById("slCreateBtn").addEventListener("click", createRoom);
document.getElementById("slJoinBtn").addEventListener("click", joinRoom);
document.getElementById("slStartBtn").addEventListener("click", startRoom);
slRestartBtn.addEventListener("click", restartRoom);
buildBoard();
if (roomCode) { slRoomCode.value = roomCode; startPolling(); pollRoom(); }

// ---------------- Real or Myth ----------------
const romStatement = document.getElementById("romStatement");
const romResult = document.getElementById("romResult");
let currentStatementId = null;
async function loadStatement() {
  const response = await fetch("/games/api/real-or-myth/next"); const data = await response.json();
  if (data.error) return;
  currentStatementId = data.id; romStatement.textContent = data.statement; romResult.innerHTML = "";
}
async function answerRealOrMyth(answer) {
  const response = await fetch("/games/api/real-or-myth/answer", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({id:currentStatementId, answer})});
  const data = await response.json();
  romResult.innerHTML = `<div class="alert alert-${data.correct ? "success" : "warning"}">${data.correct ? "Correct!" : "Not quite."} +${data.points_earned || 0} points<br>${data.explanation || ""}</div>`;
  setTimeout(loadStatement, 1500);
}
document.getElementById("romRealBtn").addEventListener("click", () => answerRealOrMyth("real"));
document.getElementById("romMythBtn").addEventListener("click", () => answerRealOrMyth("myth"));
loadStatement();

// ---------------- Treasure Hunt ----------------
const thRiddle = document.getElementById("thRiddle"); const thResult = document.getElementById("thResult"); let currentHint = "";
async function loadClue() { const response = await fetch("/games/api/treasure-hunt/current"); const data = await response.json(); if (data.treasure_found) { thRiddle.textContent = "🏆 You already found the treasure! Well done."; document.getElementById("thAnswer").disabled=true; document.getElementById("thSubmitBtn").disabled=true; return; } thRiddle.textContent=data.riddle; currentHint=data.hint; thResult.innerHTML=""; }
document.getElementById("thHintBtn").addEventListener("click", () => { thResult.innerHTML=`<div class="feedback">Hint: ${currentHint}</div>`; });
document.getElementById("thSubmitBtn").addEventListener("click", async () => { const answer=document.getElementById("thAnswer").value; const response=await fetch("/games/api/treasure-hunt/answer",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({answer})}); const data=await response.json(); if(data.correct){thResult.innerHTML=`<div class="alert alert-success">Correct! +${data.points_earned} points</div>`;document.getElementById("thAnswer").value="";if(data.treasure_found)thRiddle.textContent="🏆 Treasure found! You completed the hunt.";else setTimeout(loadClue,1200);}else thResult.innerHTML=`<div class="alert alert-warning">Not quite -- try again or check the hint.</div>`; });
loadClue();
