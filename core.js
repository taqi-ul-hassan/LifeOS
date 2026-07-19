export const initialState = {
  focusMinutes: 42,
  energy: 78,
  tasks: [
    { id: "t1", title: "Review LifeOS architecture", time: "09:30", complete: false },
    { id: "t2", title: "Deep work: product prototype", time: "11:00", complete: false },
    { id: "t3", title: "Call Mum", time: "18:30", complete: false }
  ],
  habits: [
    { name: "Sleep", value: "7h 24m", target: "8h", status: "steady" },
    { name: "Movement", value: "4,820 steps", target: "8,000", status: "needs-attention" },
    { name: "Water", value: "5 / 8 glasses", target: "8", status: "on-track" }
  ],
  insights: [
    { type: "Capacity", text: "Your most reliable focus window is 09:00–11:30." },
    { type: "Health", text: "Sleep was solid. Keep today’s plan ambitious but bounded." },
    { type: "Relationships", text: "Mum has not heard from you in 12 days." }
  ]
};

export function reduce(state, action) {
  if (action.type === "COMPLETE_TASK") {
    return { ...state, tasks: state.tasks.map(t => t.id === action.id ? { ...t, complete: true } : t) };
  }
  if (action.type === "ADD_TASK") {
    const title = action.title.trim();
    if (!title) return state;
    return { ...state, tasks: [...state.tasks, { id: `t${Date.now()}`, title, time: "Inbox", complete: false }] };
  }
  if (action.type === "CHECK_IN") {
    return { ...state, energy: Math.min(100, state.energy + 4), insights: [{ type: "Check-in", text: "Energy updated. The plan remains realistic for today." }, ...state.insights] };
  }
  if (action.type === "START_FOCUS") return { ...state, focusMinutes: state.focusMinutes + 25 };
  return state;
}

export function parseCommand(input) {
  const text = input.trim();
  const taskMatch = text.match(/^(?:add|create|remind me to)\s+(.+)/i);
  if (taskMatch) return { type: "ADD_TASK", title: taskMatch[1] };
  if (/^(?:check in|log energy)$/i.test(text)) return { type: "CHECK_IN" };
  if (/^(?:focus|start focus)$/i.test(text)) return { type: "START_FOCUS" };
  return { type: "UNKNOWN", message: "Try “add review proposal”, “check in”, or “focus”." };
}
