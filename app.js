import { initialState, parseCommand, reduce } from "./core.js";

let state = structuredClone(initialState);
const API_URL = localStorage.getItem("lifeosApiUrl") || "http://localhost:8000";
const authHeaders = () => localStorage.getItem("lifeosToken") ? { "Authorization": `Bearer ${localStorage.getItem("lifeosToken")}`, "Content-Type": "application/json" } : null;
const $ = selector => document.querySelector(selector);
const taskList = $("#taskList");
const habitList = $("#habitList");
const insightList = $("#insightList");
const feedback = $("#commandFeedback");

function render() {
  taskList.innerHTML = state.tasks.map(task => `<label class="task ${task.complete ? "complete" : ""}"><input type="checkbox" data-task="${task.id}" ${task.complete ? "checked" : ""}><span class="check"></span><span class="task-title">${task.title}</span><time>${task.time}</time></label>`).join("");
  habitList.innerHTML = state.habits.map(habit => `<div class="habit"><div><span class="habit-name">${habit.name}</span><span class="habit-value">${habit.value}</span></div><div class="meter"><span style="width:${habit.name === "Sleep" ? 92 : habit.name === "Movement" ? 60 : 63}%"></span></div><span class="habit-target">${habit.target}</span></div>`).join("");
  insightList.innerHTML = state.insights.slice(0, 3).map(item => `<div class="insight"><span class="insight-type">${item.type}</span><p>${item.text}</p></div>`).join("");
  $("#focusStat").textContent = `${state.focusMinutes} focused min this week`;
}

function dispatch(action) {
  state = reduce(state, action);
  render();
}

async function syncTask(task) {
  const headers = authHeaders();
  if (!headers) return;
  const response = await fetch(`${API_URL}/v1/tasks`, { method: "POST", headers, body: JSON.stringify({ title: task.title, priority: 3 }) });
  if (!response.ok) throw new Error("LifeOS API rejected the task");
}

$("#commandForm").addEventListener("submit", event => {
  event.preventDefault();
  const command = parseCommand($("#commandInput").value);
  if (command.type === "UNKNOWN") feedback.textContent = command.message;
  else { dispatch(command); if (command.type === "ADD_TASK") syncTask(command).catch(() => { feedback.textContent = "Captured locally. Sign in to LifeOS API to sync."; }); feedback.textContent = command.type === "ADD_TASK" ? `Captured: ${command.title}` : command.type === "CHECK_IN" ? "Check-in saved. Your plan is still balanced." : "Focus mode started. Your next 25 minutes are protected."; }
  $("#commandInput").value = "";
});

taskList.addEventListener("change", event => { if (event.target.dataset.task) dispatch({ type: "COMPLETE_TASK", id: event.target.dataset.task }); });
$("#focusButton").addEventListener("click", () => { dispatch({ type: "START_FOCUS" }); feedback.textContent = "Focus mode started. Notifications are batched for the next 25 minutes."; });
$("#checkinButton").addEventListener("click", () => { dispatch({ type: "CHECK_IN" }); feedback.textContent = "Check-in saved. Your plan is still balanced."; });
$("#addTaskButton").addEventListener("click", () => { $("#commandInput").focus(); $("#commandInput").placeholder = "add your new intention…"; });
$("#themeToggle").addEventListener("click", () => document.body.classList.toggle("dark"));
document.addEventListener("keydown", event => { if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") { event.preventDefault(); $("#commandInput").focus(); } });
render();

// The onboarding client sets lifeosToken after POST /v1/auth/token; then captures sync automatically.
