---
name: brainstorm-intake
description: Pre-plan requirements intake for new features, modules, and overhauls. Claude invokes this inline to ask targeted questions before writing any plan. Covers frontend and backend. Output feeds directly into plan writing.
---

# Brainstorm Intake

Claude invokes this skill inline — not as a dispatched subagent. The value is the human's answers, not an agent's analysis.

## When to Invoke

**INVOKE** when the request is:
- A new page, route, or screen
- A new backend module, engine method, or API endpoint
- A complete overhaul of existing behaviour
- Any task where the design or data contract is unclear

**SKIP** when the request is:
- A bug fix (use systematic-debugging instead)
- A minor tweak touching ≤ 3 files with a clear spec
- A refactor with no behaviour change
- A styling or copy fix

If in doubt — invoke. A 5-minute intake costs far less than a plan built on wrong assumptions.

---

## Step 1 — Identify Scope

Determine if the request is frontend, backend, or both. State it explicitly before asking questions:

> "This looks like a [frontend / backend / full-stack] task. Let me ask a few questions before writing the plan."

For full-stack: run both question sets. Backend questions first (API contract must exist before frontend can be specced).

---

## Step 2 — Ask Questions

Do not dump all questions at once. Ask them conversationally. If the human's answer to one question makes another irrelevant, skip it.

### Frontend Questions

1. **Job to be done.** What does the user accomplish on this page or with this component? One sentence.

2. **Data source.** What data does it display — from which existing API endpoint, or does this need a new one? If new, what does the response shape look like?

3. **States.** What does the page show when: loading, error returned, no data / empty results, data loaded? Any conditional panels that appear/disappear?

4. **URL state.** Do any filter or selection values need to survive a page refresh or be shareable via URL? If yes, which params?

5. **Design reference.** Is there a Stitch mockup, a screenshot, or just a verbal description? If Stitch — what is the project/screen name or ID?

6. **Composition.** Which existing components, pages, or layouts does this sit next to or reuse? Any known conflicts with what's already built?

7. **Done criteria.** What does passing F4 visual acceptance look like — what routes do we navigate to, and what specific things do we eyeball?

8. **Edge cases.** Any known edge cases? (no results, single-item list, very long text, mobile-width, permission gates)

### Backend Questions

1. **Output in one sentence.** What is this computing or returning? Pretend you are describing the API response to a frontend developer.

2. **Layer placement.** Which layer does this live in?
   - Engine (`formats/odi/engines/`) — pure computation
   - Calculator (`core/calculators/`) — data aggregation
   - Service — orchestration
   - Context builder wiring (`api/context_builder.py`) — param/data plumbing
   - API only (`api/`) — serialization or new endpoint

3. **Inputs.** What are the required context fields? What are the optional ones? Are any of these new params that need adding to `manifest.py`?

4. **Data reads.** What does it read from the database? Which table(s) — balls, matches, players, venues? Any joins or computed columns?

5. **Registered file risk.** Does this require touching any of: `core/data_access.py`, `core/interfaces/team_types.py`, `api/serializers.py`? If yes — why, and is there a way to avoid it?

6. **Dirty data cases.** What should happen when: a player has no balls faced (DNB), a match was abandoned, an innings is missing, the squad is empty? Silence, zero, or error?

7. **Output schema.** What does the return look like? Sketch the TypedDict or Pydantic field names and types — even rough is fine.

8. **Performance profile.** Does this run once per API call, once per match, or once per ball? On this hardware (Ryzen 5 3500U, ~4GB RAM) — is there a loop risk?

---

## Step 3 — Synthesise

After the human answers, write a brief spec confirmation back to them before touching any plan file:

```
Based on what you've described:
- [What it does, one sentence]
- [Key inputs and outputs]
- [Any constraints or risks flagged]
- [Design reference or done criteria]

Does this match what you want? Any corrections before I write the plan?
```

Do not proceed to plan writing until the human explicitly confirms.

---

## Step 4 — Hand Off

Once confirmed, tell the human:

> "Got it. Writing the plan now."

Then proceed with Claude writing `workflow/plan.md` directly — no subagent, no writing-plans skill, no REQUIRED SUB-SKILL directive in the plan file.
