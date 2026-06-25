# Loupe — Product Requirements (v1)

> Messy in, sharp out. The design critic startups don't have time to convene.

**One-liner.** Throw in raw, unstructured user-research material (tickets, Figma links, call notes, screenshots) and get back one clear, visual, opinionated report: what's wrong, why, and what to do — at the depth you choose.

**Who.** Founders and small teams with real user signal but no time, no researcher, and no senior-design crit in the room.

**The bet.** The value isn't summarizing data — anything can do that. It's the *critique*: visible design reasoning that earns trust, plus the decisiveness to commit to one verdict.

---

## 1. The core contract — the spine

Every report, at every depth, is the **same five movements in this fixed order**. This is a hard contract, not a template — the report reads top-to-bottom as a single argument: *claim → evidence → because → therefore.*

| # | Section | Job | Rule |
|---|---------|-----|------|
| 1 | **The Verdict** | The 8-second read | **One falsifiable sentence + a confidence signal.** Never a paragraph, never a hedge. If it can't commit, it must say what it's missing. |
| 2 | **Inputs** | Earn trust | Transparent strip of what was read + freshness. Skimmable, not a table. |
| 3 | **Signals** *(the See)* | What we saw | 3–5 clustered themes, each with a count, a representative quote, and a link back to source. |
| 4 | **Critique Panel** *(the Diagnose)* | Why it's broken — **the moat** | Written as a critic *speaking*, not a `What/Why/Who` form. Each card: observed friction → design reasoning (heuristic/flow/mental-model) → severity + who it hits. |
| 5 | **Next Steps** *(the Decide)* | What to do | Ranked by impact ÷ effort. Each action **back-references** the signal or critique it came from. 2–3 "this week", a couple "explore". |

**Unbroken-chain rule:** every Next Step must trace to a Critique; every Critique to a Signal; every Signal to a source. No orphan recommendations. Depth changes resolution, never the order.

---

## 2. Confidence system

Confidence is a first-class output, shown as a **stamped seal** on the Verdict and per Critique card.

- **The ceiling is set at intake.** Each answered question and added source raises the *maximum* confidence Loupe may claim. Tiers: `provisional → fair → strong → high`.
- **Caps at ~96, never 100.** A critic who claims certainty isn't trustworthy. On-brand: the loupe exists to find the flaw.
- **Anything resting on a drafted (not provided) persona is capped lower** and visibly flagged as an assumption.
- Per-claim confidence reflects source agreement ("3 sources, one story" = high; single ticket = provisional).

---

## 3. The intake — a guided interview, not a form

Loupe interviews you before it looks. Each answer is a **dial on the output**, and visibly lifts the confidence ceiling.

| Field | Type | What it adapts downstream |
|-------|------|---------------------------|
| **The brief** ("what do you need to see?") | free text | Becomes the Verdict target |
| **Company stage** | single-select | Early → signal/speed, fewer caveats · Series A+ → rigor, statistical framing |
| **Project stage** | single-select | "Exploring" → next steps are questions · "Live & on fire" → next steps are ranked fixes |
| **Personas** | have / rough / none | "None" → Loupe drafts provisional personas, caps & flags anything resting on them |
| **Raw material** | uploads + links + source chips | Each angle added raises the ceiling |
| **Concerns** | multi-select, optional | Reorders Signals/Critique to lead with flagged areas (without ignoring the rest) |

---

## 4. Depth modes

Same five-section spine; depth adds resolution, never reorders the argument.

- **Quick notes** — Verdict + Next Steps only, plain text, no charts. *Slack-paste before standup.*
- **Standard** — all 5 sections, one critique card per top signal.
- **Deep + visual** — per-signal charts, every critique card, severity, inline source links. *The attach-to-a-doc artifact.*

---

## 5. Cost & latency rules (defaults, stated to the user)

- **Links read by reference** — pull structure/metadata, never download/render the whole thing.
- **Big exports sampled, not fully read** — cluster a representative sample, count the rest by keyword. The primary cost lever; stated in intake so it reads as honest, not a shortcut.
- **Vision is opt-in** — screenshots image-processed only when the brief needs them.
- **No background pre-processing** — nothing is read until run, and only what's relevant to the brief. Uploading costs nothing until used.

---

## 6. Voice & restraint (a design principle, not decoration)

The personality is the senior designer leaning over your shoulder — not a SaaS dashboard.

- **One serif, one accent color per report.** Verdict and section heads in serif; critique as a pull-quote in the critic's voice.
- **Confidence as a stamp, not a pill.** A staked claim, not metadata.
- **Authorship** — masthead, "filed from…", a sign-off. Output is never anonymous.
- **Protect the emptiness.** A second font or a filled margin collapses it back to generic. Restraint is the feature.

---

## 7. Non-goals (v1)

- Not a live analytics dashboard — it's a point-in-time *read*.
- Not a research repository or tagging tool.
- No multi-step survey/interview *collection* — it works with what you already have.
- Does not auto-implement fixes — it advises and decides; humans act.

## Success metric

A founder reads the Verdict in 8 seconds, trusts the Critique enough to act, and ships at least one Next Step that week — without having convened a crit or compiled a report.
