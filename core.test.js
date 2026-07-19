import test from "node:test";
import assert from "node:assert/strict";
import { initialState, parseCommand, reduce } from "./core.js";

test("commands turn natural language into a task action", () => {
  assert.deepEqual(parseCommand("add renew passport"), { type: "ADD_TASK", title: "renew passport" });
});

test("completing a task preserves the rest of the state", () => {
  const next = reduce(initialState, { type: "COMPLETE_TASK", id: "t1" });
  assert.equal(next.tasks.find(task => task.id === "t1").complete, true);
  assert.equal(next.tasks.length, initialState.tasks.length);
});

test("blank tasks are ignored", () => {
  assert.equal(reduce(initialState, { type: "ADD_TASK", title: "  " }), initialState);
});
