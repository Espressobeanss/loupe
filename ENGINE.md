# Loupe — Engine Spec (v1)

How raw input becomes a `Report`. Companion to [PRD.md](PRD.md). The PRD is the contract; this is the build.

---

## 1. The pipeline

Five passes, mirroring the five-section spine. Each pass produces one part of the `Report` object and feeds the next — the same unbroken chain the report shows the user.

```
ingest → cluster → diagnose → conclude → translate
  │         │          │          │           │
 raw     Signals    Critiques   Verdict    NextSteps
 input              (+severity) (+confidence) (role-shaped)
```

1. **Ingest** — normalize sources to text + counts. Cost-controlled (§4).
2. **Cluster** — group raw items into 3–5 Signals; each gets a count, a representative quote, and `sourceRefs`.
3. **Diagnose** — the critic pass. For each Signal: name the design reasoning (heuristic violated / flow break / mental-model mismatch), severity, and who it hits. Writes in the critic's *voice*, not a form.
4. **Conclude** — synthesize the single Verdict (one falsifiable sentence) and set confidence, clamped by the intake ceiling (§3).
5. **Translate** — turn Critiques into NextSteps **shaped by the user's role** (§5). This pass is what makes one engine serve six roles.

---

## 2. Data model

```ts
Report {
  verdict:   { claim: string, confidence: Confidence, sourceRefs: ID[] }
  inputs:    { source: string, count: number, freshness: string }[]
  signals:   { id: ID, theme: string, count: number, quote: string, sourceRefs: ID[] }[]
  critiques: { id: ID, signalRef: ID, voice: string, principle: string,
               severity: 'low'|'med'|'high', who: string, confidence: Confidence }[]
  nextSteps: { text: string, ownerRole: Role, horizon: 'now'|'week'|'explore',
               impact: 1-5, effort: 1-5, critiqueRef|signalRef: ID,
               handoff?: { toRole: Role, text: string } }[]
  meta:      { role: Role, ceiling: Confidence, depth: Depth, assumptions: string[] }
}

Confidence = 'provisional' | 'fair' | 'strong' | 'high'
Role       = 'founder' | 'product' | 'design' | 'engineering' | 'ops' | 'growth'
Depth      = 'quick' | 'standard' | 'deep'
```

**Invariants the engine must enforce (not the prompt — the code):**
- Every `nextStep` has a `critiqueRef` or `signalRef`. No ref → invalid, regenerate. *(the unbroken chain)*
- Every `critique.signalRef` resolves to a real Signal; every `signal.sourceRefs` to real ingested sources.
- No `confidence` exceeds `meta.ceiling`. Anything resting on a drafted persona is capped one tier lower and its id is listed in `meta.assumptions`.
- `verdict.claim` is one sentence. Reject paragraphs at validation, not by asking nicely.

---

## 3. Confidence

Set the ceiling at intake, clamp every claim to it.

```
ceiling = f(brief filled, role set, stage set, personas, # source types, source agreement)
  provisional < fair < strong < high      // never 'certain' — cap at 'high'
```

- Per-claim confidence = source agreement. 3 sources concurring → high; single ticket → provisional.
- Drafted (not provided) persona → any claim depending on it drops one tier and is flagged.
- The ceiling is a hard clamp in `conclude` and `diagnose`, so honesty can't be prompted away.

---

## 4. Ingest — cost & latency rules (defaults)

| Input | Rule | Why |
|---|---|---|
| Links (Figma, Notion, docs) | Read structure/metadata by reference; don't download/render whole | Cheap, fast |
| Large text exports (tickets, CSV) | Cluster a representative **sample**, count the rest by keyword | The main cost lever — never send every row to the model |
| Images / screenshots | Vision-process **only** when the brief needs them | Most expensive input; never speculative |
| Everything | No background pre-processing — read on run, only what's relevant | Upload costs nothing until used |

Surface the sampling in the UI ("read a sample, counted the rest") — transparency makes it read as honest, not as a shortcut.

---

## 5. Role translation — same diagnosis, different lever

The `translate` pass takes each Critique and emits NextSteps in the role's verbs and altitude. When the root fix is outside the role's lever, emit an interim step the role *can* do now, plus a `handoff` to the role who owns the fix.

| Role | Lever / altitude | Verb set | Adds |
|---|---|---|---|
| **founder** | decisions & trade-offs | decide / ship / cut | what to do this week, the trade-off |
| **product** | roadmap & specs | prioritize / spec / measure | impact ÷ effort rank, a metric to watch |
| **design** | flows & screens | redesign / reorder / clarify | which screen, which heuristic |
| **engineering** | implementation | fix-now / rework / instrument | effort estimate, what to log |
| **ops / cx** | comms & process | pre-empt / macro / triage / escalate | what to tell users now, + handoff |
| **growth** | messaging & funnel | reframe / test / reposition | what to A/B |

Worked example — Critique: *"fee surfaces too late, reads as hidden."*
- product → "Spec fee-on-pricing-screen, rank #1, watch checkout completion."
- ops → now: "Add pre-checkout fee note to the checkout macro." handoff→product: "surface the fee on the pricing screen."

The diagnosis is computed **once**; only `translate` is role-conditioned. Switching role re-runs one cheap pass, not the whole report.

---

## 6. Prompt architecture

One model call per pass (cluster / diagnose / conclude / translate); ingest is mostly code. Each call gets only what it needs:

- **cluster**: sampled raw text + brief + concerns → Signals (forced to JSON schema).
- **diagnose**: Signals + personas + ceiling → Critiques. System prompt carries the critic voice + heuristic vocabulary; ceiling passed as a hard cap.
- **conclude**: Critiques + brief → one Verdict + confidence ≤ ceiling.
- **translate**: Critiques + role → NextSteps with handoffs. Role rubric (§5) injected as the system prompt.

Schema-forced output at each step → validate invariants (§2) in code → regenerate the single failing pass, not the whole report. Depth (`quick`/`standard`/`deep`) is a render-time filter over the same object — never a different generation.
