# SKILL: guide-quality
# Agent: Gemini
# When: After implementing a guide page, before committing (replaces manual review)
# Purpose: Validate guide pages meet the trading terminal standard — not a marketing page

---

## GEMINI EXECUTION STEPS

### Step 1 — Read the guide page
Read the implemented guide page in `frontend/app/docs/[feature]/page.tsx`.
Read any components in `frontend/components/guide/` used by this page.

### Step 2 — Run quality checks

**Trading narrative check:**
Does the guide answer all five questions?
1. What is this feature? (one sentence, factual)
2. How is it calculated? (data-grounded, references actual fields — no ghost fields)
3. What does it tell the trader? (specific trading decision, not generic)
4. How do you read it? (UI walkthrough referencing actual component elements)
5. When do you act on it? (entry/exit signal context, not vague advice)

For each question: ANSWERED or MISSING.

**Ghost field check:**
Does the guide reference any field not present in the actual API response?
Read `frontend/lib/types.ts` to confirm every field mentioned in the guide exists.
Ghost fields: any field mentioned in the guide that is not in the TypeScript types.

**Tone check:**
Is the language precise and functional (trading terminal) or vague and aspirational (marketing)?
Flag any sentence containing: "powerful", "comprehensive", "seamlessly", "robust",
"cutting-edge", "state-of-the-art", "intuitive", or any sentence that doesn't state
a specific fact or instruction.

**Visual check (Playwright):**
Take a Playwright screenshot of the guide page at localhost:3000/docs/[feature].
Does it look like a professional reference document?
Flag: excessive whitespace, decorative elements, non-monospace data values, missing sections.

### Step 3 — Write quality report
Write to `agents/workflow/reports/guide-quality-<feature>.json`:
```json
{
  "audit": "guide-quality",
  "feature": "<feature name>",
  "date": "YYYY-MM-DD",
  "verdict": "PASS | FAIL",
  "trading_narrative": {
    "what_is_it": "ANSWERED",
    "how_calculated": "ANSWERED",
    "what_it_tells": "ANSWERED",
    "how_to_read": "MISSING",
    "when_to_act": "ANSWERED"
  },
  "ghost_fields": [],
  "tone_violations": [],
  "visual": "PASS",
  "screenshot_path": "agents/workflow/screenshots/guide-<feature>.png",
  "issues": []
}
```

verdict is PASS only if:
- All 5 narrative questions are ANSWERED
- No ghost fields
- No tone violations
- Visual is PASS

---

## NOTES

- A guide that passes gates (F1/F2/F3) but fails this quality check has technically correct
  code but useless content. Gates don't catch content quality — this skill does.
- Ghost fields are a hard FAIL — they tell the trader to look for data that doesn't exist.
