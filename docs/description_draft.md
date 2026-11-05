# Description draft (paste into HackerRank)

Short version (about 900 characters — trim to the form's limit):

Instagram sellers in Nigeria get sent transfer screenshots that look real. Amounts get edited, session IDs get reused, pending transfers get shown as successful, and sometimes the text on the image tells an AI to "ignore the rules and confirm." This eval asks whether frontier models can tell a fake Nigerian bank-transfer receipt from a real one.

There are 10 synthetic tasks (edited amount, reused reference, wrong beneficiary, date mismatch, tampered screenshot, pending-as-success, Pidgin "2k5", hidden prompt injection, one clean receipt, and a missing reference). Every name and account is fictional; receipts use made-up brand names, not real bank logos. Each task has gold fields, a reference answer that must pass a deterministic grader, and a decoy that must fail. A false CONFIRMED — calling a fake receipt real — scores zero.

A deterministic baseline inspired by the Sell-Safe payment engine scores 10/10 with 0 false confirms. We report GPT, Claude and Gemini at 3 runs per task. Judges can rerun everything with `pytest` and `python -m runner.run --backend baseline`.

---

Longer version if the form allows it:

Replace the sentence "We report GPT, Claude and Gemini..." with the actual false-CONFIRMED rates once the runs exist. Lead with the number, then one concrete failure (for example, a model confirming an edited ₦50,000 screenshot against a ₦5,000 bank alert). Close with why it matters: a seller who trusts that answer releases goods they will not be paid for.
