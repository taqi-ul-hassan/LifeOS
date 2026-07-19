from concurrent.futures import ThreadPoolExecutor


def run_steps(steps: list[dict], action_runner, payload: dict) -> list[dict]:
    results = []
    for step in steps:
        if step.get("mode") == "parallel":
            with ThreadPoolExecutor(
                max_workers=min(4, len(step.get("actions", [])))
            ) as pool:
                results.extend(
                    pool.map(
                        lambda action: action_runner(action, payload),
                        step.get("actions", []),
                    )
                )
        elif step.get("condition") and not step["condition"](payload):
            continue
        else:
            results.append(action_runner(step, payload))
    return results
