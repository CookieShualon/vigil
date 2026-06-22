---
target: templates/index.html
total_score: 25
p0_count: 0
p1_count: 3
timestamp: 2026-06-22T11-13-00Z
slug: templates-index-html
---
#### Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Strong status columns, counts, dots, elapsed timers, and screenshot updates; weak submit/loading feedback after task creation. |
| 2 | Match System / Real World | 3 | Good operator language, but cookie JSON and raw model names assume technical comfort. |
| 3 | User Control and Freedom | 2 | Cancel/Esc exists, but Stop and cookie delete are immediate with no confirmation or undo. |
| 4 | Consistency and Standards | 3 | Cohesive visual vocabulary, but inline styles and incomplete focus states weaken consistency. |
| 5 | Error Prevention | 1 | Destructive actions and cookie import validation have too little prevention. |
| 6 | Recognition Rather Than Recall | 2 | Main actions are visible, but drag-to-requeue and keyboard shortcuts are hidden knowledge. |
| 7 | Flexibility and Efficiency | 2 | Useful shortcuts exist, but keyboard/accessibility and batch/power paths are incomplete. |
| 8 | Aesthetic and Minimalist Design | 3 | Calm density works; empty states and raw action JSON create noise. |
| 9 | Error Recovery | 2 | Some inline errors exist, but failures do not guide the operator toward recovery. |
| 10 | Help and Documentation | 2 | README is strong, but in-product contextual help is thin. |
| **Total** | | **25/40** | **Acceptable: solid foundation, significant UX hardening needed.** |

#### Anti-Patterns Verdict

**LLM assessment**: Low-to-moderate AI slop risk. Vigil does not read as generic SaaS AI output; the graphite palette, compact mono type, Kanban lifecycle, semantic state colors, and manual-control frame are coherent with the Soft Control Room direction. The bigger risk is that the interface can become too terse and terminal-like for AI operators: empty columns say only `empty`, failures show raw strings, and account setup asks for pasted cookie JSON with limited reassurance.

**Deterministic scan**: The detector found 13 items in `templates/index.html`: one layout-property animation warning at line 350, one single-font warning at line 34, and 11 design-system drift advisories for undocumented colors/radii. The single-font finding is a false positive for this product register because `DESIGN.md` intentionally specifies JetBrains Mono across roles. The layout transition is valid: animating `right` and `width` on the detail panel can jank. Several design-token advisories are useful cleanup signals, especially repeated `2px` scrollbar radii and literal overlay/black/white colors.

**Visual overlays**: No reliable user-visible overlay is available in this environment because no browser automation tool is available to open a fresh tab, inject the detector script, and read console messages. The CLI detector did run successfully.

#### Overall Impression

Vigil has a strong foundation: it feels like a real operator surface, not a decorative AI dashboard. The biggest opportunity is recovery guidance. The UI tells you that work is queued/running/paused/failed, but it does not yet teach what to do when the board is empty, a task fails, or an account import is risky.

#### What's Working

- The five-column queue/running/paused/done/failed structure maps directly to the agent lifecycle and gives operators a fast mental model.
- Manual takeover is the most polished interaction: the amber paused state, expanded detail panel, manual badge, keyboard hint, and Give Back Control action make the handoff flow understandable.
- The visual system is coherent: graphite surfaces, one guide-light accent, semantic state colors, thin borders, and compact mono typography all support the product purpose.

#### Priority Issues

**[P1] Accessibility and focus semantics are underbuilt**

**Why it matters**: This is an operator tool. Keyboard and screen-reader users need reliable control during high-stakes handoffs.

**Fix**: Add dialog semantics and labels, accessible close button names, focus trapping/restoration, consistent `:focus-visible`, and non-color status cues.

**Suggested command**: `/impeccable audit templates/index.html`

**[P1] Destructive actions lack friction**

**Why it matters**: Stopping an active browser task or deleting saved account cookies can interrupt expensive or fragile work.

**Fix**: Add lightweight confirmation or undo for Stop and cookie delete, with copy that clarifies consequences.

**Suggested command**: `/impeccable harden templates/index.html`

**[P1] Empty and error states do not teach recovery**

**Why it matters**: Vigil promises supervision and recovery without reading logs. Current empty/failure copy gives almost no next step.

**Fix**: Replace generic `empty` placeholders with state-specific copy; add actionable failure panels with Retry, relevant context, and guidance for login/2FA/manual-control situations.

**Suggested command**: `/impeccable onboard templates/index.html`

**[P2] Key workflows rely on hidden knowledge**

**Why it matters**: Drag-to-requeue and keyboard shortcuts exist, but operators will not discover them from the UI.

**Fix**: Surface subtle hints in failed/empty states, modal footer copy, and column headers.

**Suggested command**: `/impeccable clarify templates/index.html`

**[P2] Mobile and responsive behavior is structurally fragile**

**Why it matters**: Fixed sidebar, five fixed columns, fixed-width modals, and `overflow: hidden` will collapse poorly outside desktop.

**Fix**: Define tablet/mobile behavior: collapsible sidebar, horizontally scrollable or stacked lanes, full-width dialogs, and panel widths that fit the viewport.

**Suggested command**: `/impeccable adapt templates/index.html`

#### Persona Red Flags

**Alex (Power Operator)**: `n` and Cmd/Ctrl+Enter shortcuts exist, but the UI does not reveal them. Drag-to-requeue is implemented but invisible until learned from documentation. Alex can move fast only after reading the README or source.

**Sam (Accessibility-Dependent User)**: Modals lack proper dialog semantics, close controls are symbol-only, many hover styles lack corresponding focus-visible styles, and status dots rely heavily on color. The primary flow may be difficult with keyboard-only or screen-reader navigation.

**Jordan (First-Time AI Operator)**: Account setup is intimidating. The Accounts modal asks for raw cookie JSON and extension names, but does not do enough to reassure Jordan about local storage, domain scope, or what valid input looks like.

#### Minor Observations

- `--muted: #666666` is used broadly for labels and placeholders; several instances are likely too low-contrast for WCAG AA on near-black panels.
- Inline styles in the modal/account/detail markup make the design harder to maintain.
- The report section uses guide-light for every heading, which can overuse the accent on long reports.
- The detector's `single-font` warning should be ignored for this product: one mono family is intentional and documented.
- The detail panel transition animates layout properties; use transform-based drawer movement where possible.

#### Questions to Consider

- What if the empty board felt like a calm launchpad instead of five dead columns?
- Should Stop be instant, or should Vigil protect operators from accidentally killing fragile browser work?
- Is raw cookie JSON acceptable for the intended operator, or should account setup feel more like a guided import?
- What would make a paused handoff feel unmistakably safe: clearer browser controls, a checklist, or a stronger agent-is-waiting state?
