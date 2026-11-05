# Skill: eval design (micro1 receipt suite)

## When to use

Any time you add, edit or drop a task, change a gold label, or write about what the eval "proves."

## Rules

1. A task is a JSON file in `tasks/` plus a row in `tasks/catalog.json`. Never leave an orphan file.
2. Every task needs: `prompt`, `image_spec`, `evidence`, `gold`, `reference_answer`, `decoy_answer`.
3. `reference_answer` equals `gold` and must pass the grader. `decoy_answer` must fail. If gold is not `CONFIRMED`, the decoy should be a false `CONFIRMED` so the catastrophic path stays tested.
4. Keep the suite inside 8–10 tasks. Adding an 11th means dropping or merging something — micro1 asked for 5–10 quality tasks, not a dump.
5. Gold must be uniquely justified by `evidence`. If two verdicts are reasonable, the prompt is underspecified: fix the prompt or the evidence, do not "pick the harsher gold to make models look worse."
6. All people, banks, account traces and references are fictional. Brand names on the image are HorizonPay, GulfTrust Bank, Harbor MFB, PointBridge. Never paste a real logo file.
7. Every rendered PNG must include the disclaimer already in `generator/receipts.py`.
8. After any gold change: `python -m pytest -q` and `python -m runner.run --backend baseline --runs 1`. Baseline must stay 10/10 with 0 false CONFIRMED, or you write down why it changed.
9. Expected failure modes live on the task (`expected_failure_mode`) so the write-up can be checked against transcripts later.

## Good task shape

- One primary trick (edited amount, reused reference, …)
- One set of bank evidence that a careful reader can use
- A control somewhere else in the suite so "always SUSPICIOUS" cannot ace it (T07, T09)

## Bad task shape

- Real customer receipts
- A trick that depends on pixels the runner never sends (unless you also attach the image and say so)
- Ambiguous informal amounts without a gold conversion (`2k5` = 2500 is already specified)
