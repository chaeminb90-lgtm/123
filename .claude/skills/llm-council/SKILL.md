---
name: llm-council
description: Run a three-stage council that produces independent answers, anonymous peer rankings, and a chairman synthesis.
argument-hint: "<question>"
disable-model-invocation: true
user-invocable: true
---

# LLM Council

Treat `$ARGUMENTS` as the user's complete question. If it is empty, ask for one question and stop.

Complete all three stages below. Do not replace the council with your own direct answer. Do not assign personas such as critic, first-principles thinker, or implementer. Every member in a stage receives the same task.

## Stage 1: independent answers

Launch exactly four independent general-purpose subagents in parallel with the Agent tool. Make all four calls before waiting for results. Do not show one member another member's answer.

Send each member the exact user question and this common instruction:

> Answer independently in 400 words or fewer. Optimize for factual accuracy and useful insight. State important assumptions and uncertainties. Support factual claims with evidence when tools or supplied context allow it. Do not discuss this council or guess what other members may say.

Request these model tiers for the four calls:

1. `opus`
2. `sonnet`
3. `haiku`
4. Omit the model parameter so it inherits the main conversation's model

If a requested tier is unavailable, retry that seat once with an available model. Record the requested tier and any retry. Do not claim which exact model ran unless the tool result confirms it.

After all calls return, randomly assign successful answers to `응답 A`, `응답 B`, `응답 C`, and `응답 D`. Keep the mapping private until Stage 2 is complete.

## Stage 2: anonymous evaluation

Build one evaluation packet containing the original question and the complete, verbatim labeled answers. Do not summarize or shorten them. Remove model names, requested tiers, tool call identifiers, and wording that reveals the source outside the answer itself.

Launch exactly four new general-purpose evaluation subagents in parallel. Make all four calls before waiting for results. Use the same model-tier pattern as Stage 1.

Send every evaluator the identical packet and this instruction:

> In 250 words or fewer, evaluate each response for factual accuracy and useful insight. Identify specific strengths, errors, unsupported claims, and missing considerations. Then rank all responses from best to worst with no ties. Judge the text only. Do not guess authorship. Return a short rationale followed by a final ranking in the form `응답 B > 응답 A > 응답 D > 응답 C`.

Keep every evaluation. Do not collapse rankings into a vote before the chairman sees the rationales.

## Stage 3: chairman synthesis

Launch one final general-purpose subagent as chairman. Request `opus`; if unavailable, use an available model and record the retry.

Give the chairman all of the following:

- the original question
- all labeled Stage 1 answers verbatim and in full
- all Stage 2 evaluations and rankings verbatim and in full

Send this instruction:

> In 700 words or fewer, produce the best final answer to the original question. Use the evaluations as evidence, not as a majority vote. Resolve conflicts by checking reasoning and support in the original responses. Preserve important minority insights when well supported. State remaining uncertainty and the next verification step where relevant. Do not mention model identities.

## Return the result

Return one response with these sections:

1. `## 1단계: 독립 답변` with `응답 A` through `응답 D`
2. `## 2단계: 익명 평가` with each evaluator's critique and ranking
3. `## 3단계: 의장 최종 답변` with the chairman's answer
4. `## 실행 메모` with requested model tiers, failures, and retries

If fewer than three Stage 1 answers or fewer than three Stage 2 evaluations succeed, stop and report that the council did not complete. Never invent missing responses or rankings.
