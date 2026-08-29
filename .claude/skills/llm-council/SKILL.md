---
name: llm-council
description: Convene a council of multiple models to answer one hard question — each member answers independently, then peer-reviews the others' answers anonymously, then a chairman synthesizes a final verdict. Use when the user asks to "convene the council", "ask the council", run a multi-model panel, get a second (or third) opinion, cross-examine an answer, or wants high-stakes advice where one model's answer isn't trustworthy enough — architecture decisions, design tradeoffs, risky refactors, ambiguous bug diagnoses, reviewing a plan or a piece of writing. Do NOT use for routine questions, quick lookups, or mechanical edits — the council is expensive and slow.
---

# LLM Council

One model answering alone has one set of blind spots. The council pattern
trades tokens and wall-clock time for coverage: several members answer the same
question in isolation, judge each other blind, and a chairman writes the verdict.

Isolation is the whole point. Members must not see each other's answers in
stage 1, and must not know whose answer they are grading in stage 2. Any
leakage collapses the council into one opinion with extra steps.

## When to convene

Convene when the cost of a wrong answer is high and the question is genuinely
contestable: architecture and design tradeoffs, "is this plan sound", ambiguous
diagnoses, security or data-loss risk, review of important writing.

Do not convene for anything with one correct answer you can just look up, for
mechanical edits, or when the user is in a hurry. Say plainly that the question
does not need a council and answer it directly.

## Stage 0 — Frame the question

Write the question once, as a self-contained brief. Every member gets the exact
same text; they do not share your conversation history, so inline what matters:

- The question, stated sharply enough to disagree about.
- Relevant code, with file paths and line numbers, pasted or named for reading.
- Constraints that are already settled (stack, deadline, what must not change).
- The output shape you want: a recommendation plus its strongest objection.

If the brief is vague, the council produces four vague answers and the synthesis
is mush. Spend the effort here.

## Stage 1 — Independent answers

Dispatch every member in **one message with multiple Agent calls** so they run
concurrently. Give each an identical brief and a distinct seat.

Vary the seat, not the question. Two useful axes:

- **Model** — pass a different `model` to each Agent call where more than one is
  available (e.g. `opus`, `sonnet`, `haiku`, `fable`). Different models fail
  differently, which is the diversity you are buying.
- **Stance** — a short persona that biases what each member notices: the
  implementer who has to ship it, the maintainer inheriting it in two years, the
  adversary trying to break it, the reviewer who cares about the user's actual
  goal.

Three to five members is the working range. Two is a coin flip; beyond five the
review stage gets expensive and the answers repeat.

Ask each member for: a direct recommendation, the reasoning that supports it,
its strongest failure mode, and its confidence. Tell them to say "not enough
information" rather than guess — a member that hedges honestly is worth more in
stage 2 than one that bluffs.

If a member's tools let it read the repo, say which files are in scope; a member
answering from the brief alone should be told so.

## Stage 2 — Blind peer review

Collect the answers, strip every trace of authorship, and relabel them
`Response A`, `Response B`, … in a fixed order. Remove model names, personas,
signature phrasing, and any "as the adversary, I…" framing.

Send the anonymized set back to each member (again, all Agent calls in one
message). Each reviews **all** responses, including its own — which it cannot
identify — and returns:

1. A ranking of the responses, best to worst.
2. One sentence per response on what it gets right and what it gets wrong.
3. Any claim it believes is factually false, named explicitly.

Rank on correctness and usefulness, not style or length. State that outright in
the review prompt: reviewers reward long confident prose otherwise.

Skip stage 2 only when the stage-1 answers already agree on everything that
matters — then say so and go straight to the verdict.

## Stage 3 — Chairman's verdict

You are the chairman. Do not average the rankings and crown a winner. Read the
answers and the reviews and write the verdict yourself:

- **The answer.** One clear recommendation, in your own words, drawing on
  whichever parts of whichever responses survive scrutiny.
- **Why.** The reasoning that held up under review.
- **Dissent.** Where members disagreed and what would settle it. A minority
  answer that no reviewer could refute belongs here, named as such.
- **Confidence.** Say plainly how sure the council is, and what evidence would
  change the verdict.

A unanimous council is not proof — shared training data produces shared blind
spots. If every member agrees, say the agreement was unanimous and note it is
weak evidence when they are all variants of one model family.

Never present the verdict as more certain than the reviews support, and never
silently drop a dissent because it complicates the story.

## Reporting back

Lead with the verdict. Then the disagreements, which are the most informative
output of the whole exercise. Keep per-member transcripts out of the reply
unless the user asks — offer them instead.

If the user asked for a specific member's take ("what did the adversary say?"),
quote that member directly.

## Cost

A council is roughly N + N + 1 model calls on the same context: real money and
real minutes. Convene it deliberately, tell the user when you are about to, and
prefer a smaller council over a larger one when the question is narrow.
