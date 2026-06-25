"""Loupe engine — produces a Report from raw input.

Pipeline (see ENGINE.md): ingest -> cluster -> diagnose -> conclude -> translate.

v1 is a STUB: every pass returns the prebaked "checkout read" sample so the app
runs with zero secrets and zero network. Each pass is isolated behind a function
with a TODO marking exactly where the real Claude call goes. Only `translate` is
role-conditioned — diagnosis is computed once, which is why switching role is cheap.
"""

CONFIDENCE_ORDER = ["provisional", "fair", "strong", "high"]
ROLES = ["founder", "product", "design", "engineering", "ops", "growth"]


# --- ingest -----------------------------------------------------------------
def ingest(sources):
    """Normalize sources to text + counts. Links by reference, big files sampled.
    TODO: real adapters (Zendesk/CSV/Figma metadata). Returns the sample for now."""
    return [
        {"id": "src-tickets", "source": "support tickets", "count": 47, "freshness": "2h ago"},
        {"id": "src-figma", "source": "Figma checkout flow", "count": 1, "freshness": "1d ago"},
        {"id": "src-notes", "source": "call notes", "count": 12, "freshness": "3d ago"},
    ]


# --- cluster ----------------------------------------------------------------
def cluster(inputs, brief, concerns):
    """Group raw items into 3-5 Signals. TODO: Claude call, schema-forced JSON."""
    return [
        {"id": "sig-1", "theme": '"why am I charged more?"', "count": 31,
         "quote": "I got to the end and the price was higher than advertised.",
         "weight": 100, "sourceRefs": ["src-tickets"]},
        {"id": "sig-2", "theme": "back-button at checkout", "count": 12,
         "quote": "Session replays show users backing out at the fee step.",
         "weight": 39, "sourceRefs": ["src-figma", "src-notes"]},
        {"id": "sig-3", "theme": '"I thought it was free"', "count": 8,
         "quote": "Nowhere did it say there was an admin fee.",
         "weight": 26, "sourceRefs": ["src-tickets"]},
    ]


# --- diagnose ---------------------------------------------------------------
def diagnose(signals, personas, ceiling):
    """Critic pass. TODO: Claude call carrying the critic voice + heuristic vocab.
    Confidence is clamped to `ceiling` here so honesty can't be prompted away."""
    return [
        {"id": "crit-1", "signalRef": "sig-1",
         "voice": ("The total breaks its promise. You quote one price, then change it "
                   "at the door — that's not a pricing bug, it's a trust bug. The "
                   "number isn't disclosed as it grows, so the final jump reads as a "
                   "reveal, not a sum."),
         "principle": "visibility of system status",
         "severity": "high", "who": "every first-time buyer",
         "confidence": _clamp("high", ceiling)},
    ]


# --- conclude ---------------------------------------------------------------
def conclude(critiques, brief, ceiling):
    """Synthesize one falsifiable Verdict + confidence <= ceiling. TODO: Claude call."""
    return {
        "claim": ("People bail at the admin fee. It reads as a charge you're sneaking "
                  "in at the last second."),
        "confidence": _clamp("high", ceiling),
        "sourceRefs": ["src-tickets", "src-figma", "src-notes"],
    }


# --- translate (role-conditioned) -------------------------------------------
_NEXT = {
    "founder": [
        {"h": "week", "t": "Decide: fold the fee into one all-in price, or cut it.", "ref": "follows the crit", "critiqueRef": "crit-1"},
        {"h": "week", "t": "Make the call before the next pricing change ships.", "ref": "follows back-button", "signalRef": "sig-2"},
        {"h": "explore", "t": "Sanity-check margins on all-in pricing first.", "ref": "", "critiqueRef": "crit-1"},
    ],
    "product": [
        {"h": "week", "t": 'Spec "fee on the pricing screen" — rank it #1 this sprint. Watch checkout completion.', "ref": "follows the crit", "critiqueRef": "crit-1"},
        {"h": "week", "t": 'Rename "admin fee" to what it covers.', "ref": 'follows "thought it was free"', "signalRef": "sig-3"},
        {"h": "explore", "t": "Test one all-in price vs. itemized.", "ref": "", "critiqueRef": "crit-1"},
    ],
    "design": [
        {"h": "week", "t": "Move fee disclosure onto the pricing card, not the final step.", "ref": "follows the crit", "critiqueRef": "crit-1"},
        {"h": "week", "t": "Show the running total updating across each step.", "ref": "follows back-button", "signalRef": "sig-2"},
        {"h": "explore", "t": "Prototype an all-in price layout.", "ref": "", "critiqueRef": "crit-1"},
    ],
    "engineering": [
        {"h": "now", "t": "Quick fix: render the fee in the pricing component (small lift).", "ref": "follows the crit", "critiqueRef": "crit-1"},
        {"h": "now", "t": "Add a drop-off event at the fee step so we can measure it.", "ref": "instrument", "signalRef": "sig-2"},
        {"h": "explore", "t": "Rework: pricing service to support all-in vs. itemized (larger lift).", "ref": "", "critiqueRef": "crit-1"},
    ],
    "ops": [
        {"h": "now", "t": "Add a pre-checkout fee note to the checkout macro.", "ref": "follows the crit", "critiqueRef": "crit-1"},
        {"h": "now", "t": 'Canned reply for "why am I charged more?" — name what the fee covers.', "ref": "follows top signal", "signalRef": "sig-1",
         "handoff": {"toRole": "product", "text": "surface the fee on the pricing screen."}},
        {"h": "explore", "t": "Tag fee-related tickets so we can watch the volume drop.", "ref": "", "signalRef": "sig-1"},
    ],
    "growth": [
        {"h": "week", "t": "Reframe the fee as a benefit in checkout copy.", "ref": "follows the crit", "critiqueRef": "crit-1"},
        {"h": "week", "t": 'A/B "all-in price" in the ad-to-checkout flow.', "ref": 'follows "thought it was free"', "signalRef": "sig-3"},
        {"h": "explore", "t": "Test a fee-inclusive vs. fee-added landing page.", "ref": "", "critiqueRef": "crit-1"},
    ],
}


def translate(critiques, role):
    """Turn Critiques into NextSteps in the role's lever + verbs, with hand-offs
    when the fix is outside the role's reach. TODO: Claude call with role rubric."""
    return list(_NEXT.get(role, _NEXT["product"]))


# --- orchestration ----------------------------------------------------------
def _clamp(conf, ceiling):
    return conf if CONFIDENCE_ORDER.index(conf) <= CONFIDENCE_ORDER.index(ceiling) else ceiling


def compute_ceiling(intake):
    """Map intake completeness to the highest confidence Loupe may claim.
    Caps at 'high' — never 'certain'. TODO: weight by real source agreement."""
    score = 1
    if intake.get("brief"):
        score += 1
    if intake.get("role"):
        score += 1
    score += min(len(intake.get("sources", [])), 2)
    return CONFIDENCE_ORDER[min(score, len(CONFIDENCE_ORDER) - 1)]


def build_report(role="product", depth="standard", intake=None):
    intake = intake or {"brief": "checkout drop-off", "role": role,
                        "sources": ["tickets", "figma", "notes"], "personas": "rough"}
    if role not in ROLES:
        role = "product"
    ceiling = compute_ceiling(intake)

    inputs = ingest(intake.get("sources"))
    signals = cluster(inputs, intake.get("brief"), intake.get("concerns"))
    critiques = diagnose(signals, intake.get("personas"), ceiling)   # computed once
    verdict = conclude(critiques, intake.get("brief"), ceiling)
    next_steps = translate(critiques, role)                          # role-conditioned

    return {
        "verdict": verdict,
        "inputs": inputs,
        "signals": signals,
        "critiques": critiques,
        "nextSteps": next_steps,
        "meta": {"role": role, "ceiling": ceiling, "depth": depth, "assumptions": []},
    }
