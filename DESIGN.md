---
name: Vigil
description: Calm operational dashboard for supervising LLM browser-agent tasks.
colors:
  guide-light: "#c8ff00"
  graphite-black: "#0a0a0a"
  graphite-panel: "#111111"
  graphite-raised: "#181818"
  graphite-border: "#222222"
  text-primary: "#e8e8e8"
  text-muted: "#8a8a8a"
  text-placeholder: "#9a9a9a"
  text-subtle: "#5f5f5f"
  accent-ink: "#000000"
  hover-border: "#444444"
  hover-border-strong: "#555555"
  overlay-scrim: "rgba(0, 0, 0, 0.7)"
  code-bg: "#1e1e1e"
  queue: "#888888"
  running: "#3b82f6"
  done: "#22c55e"
  failed: "#ef4444"
  paused: "#f59e0b"
typography:
  display:
    fontFamily: "JetBrains Mono, monospace"
    fontSize: "15px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.05em"
  headline:
    fontFamily: "JetBrains Mono, monospace"
    fontSize: "14px"
    fontWeight: 700
    lineHeight: 1.3
  title:
    fontFamily: "JetBrains Mono, monospace"
    fontSize: "13px"
    fontWeight: 700
    lineHeight: 1.4
  body:
    fontFamily: "JetBrains Mono, monospace"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "JetBrains Mono, monospace"
    fontSize: "10px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.1em"
rounded:
  xs: "3px"
  sm: "4px"
  md: "6px"
  lg: "8px"
  pill: "10px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "20px"
  modal: "24px"
components:
  button-primary:
    backgroundColor: "{colors.guide-light}"
    textColor: "{colors.graphite-black}"
    rounded: "{rounded.sm}"
    padding: "8px 16px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.text-muted}"
    rounded: "{rounded.sm}"
    padding: "8px 12px"
  input-field:
    backgroundColor: "{colors.graphite-raised}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.sm}"
    padding: "7px 9px"
  task-card:
    backgroundColor: "{colors.graphite-panel}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    padding: "12px"
---

# Design System: Vigil

## 1. Overview

**Creative North Star: "Soft Control Room"**

Vigil's interface is an operator room for autonomous browser work: dark, dense, and precise, but not hostile. The system uses compact mono typography, quiet graphite surfaces, and one rare guide-light accent to keep attention on task state, live browser evidence, and the next available intervention.

The design should preserve the existing operational efficiency while softening intimidation. It rejects black-box terminal theatrics, decorative SaaS gloss, and vague status presentation. Every visual choice should help an AI operator understand what is queued, running, paused, done, or failed.

**Key Characteristics:**
- Compact five-column workflow with persistent task state.
- Dark tonal surfaces separated by thin borders rather than heavy shadows.
- Rare neon-lime action color reserved for primary actions, active values, and reports.
- Semantic status colors for task lifecycle and human handoff.
- Mono-forward typography that reads as transparent and inspectable.

## 2. Colors

The palette is graphite-first with a single guide-light accent and restrained semantic status colors.

### Primary
- **Guide Light**: The primary action and focus accent. Use it for the app name, `New Task`, submit actions, active step values, report headings, and successful control handoff. It must stay rare so it keeps meaning.

### Secondary
- **Running Blue**: Live execution state and links inside reports.
- **Paused Amber**: Human handoff, manual-control mode, and operator intervention.
- **Done Green**: Successful completion, saved account confirmation, and copied report feedback.
- **Failed Red**: Task failure, destructive stop actions, and form validation errors.
- **Queue Gray**: Waiting state and neutral queue labels.

### Neutral
- **Graphite Black**: Page background and live-browser void.
- **Graphite Panel**: Sidebar, task cards, modals, and detail panel.
- **Graphite Raised**: Form fields, report bodies, detail descriptions, history rows, and count chips.
- **Graphite Border**: Column dividers, panel borders, card outlines, and low-emphasis control strokes.
- **Primary Text**: Main readable text across the dark UI.
- **Muted Text**: Labels, metadata, secondary button text, and empty states. Avoid using it for required instructions or placeholders that must be read quickly.

### Named Rules
**The Guide-Light Rarity Rule.** The primary accent should occupy less than 10% of any screen. If everything glows, nothing is actionable.

**The State Color Rule.** Blue, amber, green, red, and queue gray are semantic colors, not decoration. Do not reuse them for unrelated emphasis.

## 3. Typography

**Display Font:** JetBrains Mono (with monospace fallback)  
**Body Font:** JetBrains Mono (with monospace fallback)  
**Label/Mono Font:** JetBrains Mono

**Character:** The typography is technical but approachable because every role comes from one family. Scale changes are small; hierarchy comes from weight, casing, color, and placement rather than oversized headings.

### Hierarchy
- **Display** (700, 15px, 1.2, 0.05em): Product mark in the sidebar only.
- **Headline** (700, 14px, 1.3): Modal titles and report h1 headings.
- **Title** (700, 13px, 1.4): Detail panel title, card action labels, and compact section titles.
- **Body** (400, 13px, 1.6): Task descriptions, modal text fields, report paragraphs, and readable explanatory copy.
- **Label** (700, 10px, 0.1em, uppercase): Section labels, column labels, form labels, and compact metadata.

### Named Rules
**The Mono Transparency Rule.** Use JetBrains Mono across UI labels, controls, and data so agent actions feel inspectable. Do not introduce display fonts into product controls.

**The Compact Scale Rule.** Product UI headings stay fixed-size and compact. Do not use fluid hero typography in the dashboard.

## 4. Elevation

Vigil is mostly flat. Depth comes from tonal layering, thin borders, fixed panels, and modal overlays. Shadows may appear only as subtle operational lift for active overlays or open panels; they should never become decorative glow.

### Shadow Vocabulary
- **Overlay Scrim** (`background: rgba(0,0,0,0.7)`): Used behind modals to isolate focused work.
- **Panel Separation** (`border-left: 1px solid var(--border)` / `border-right: 1px solid var(--border)`): Used for sidebar, columns, and detail drawer instead of drop shadows.

### Named Rules
**The Flat-Until-Focused Rule.** Surfaces are flat at rest. Lift is allowed only when the user is focused on a modal, drawer, or manual-control state.

## 5. Components

### Buttons
- **Shape:** Small rectangular controls with softened corners (4px).
- **Primary:** Guide Light background with black text, bold mono label, and compact padding. Used for `New Task`, `Run Task`, `Save Account`, and give-back/retry confirmations.
- **Hover / Focus:** Hover reduces opacity or increases tinted background. Focus must be visible with a guide-light outline or border shift.
- **Secondary / Ghost:** Transparent or graphite backgrounds with muted text and a graphite border. Hover should brighten the border and text without changing component shape.

### Chips
- **Style:** Count chips use Graphite Raised with muted text and small pill radius (10px).
- **State:** Status indicators are separate colored dots, not generic chips. Keep state labels and dots visually paired.

### Cards / Containers
- **Corner Style:** Task cards use compact rounded corners (6px); modals and browser frames use a slightly larger radius (8px).
- **Background:** Cards sit on Graphite Panel; nested information blocks use Graphite Raised.
- **Shadow Strategy:** Use borders and tonal contrast first. Avoid decorative shadows on cards.
- **Border:** One-pixel graphite borders define columns, cards, modals, live-browser frames, and reports.
- **Internal Padding:** Cards use 12px; modals use 24px; detail panel sections use 16-20px rhythm.

### Inputs / Fields
- **Style:** Graphite Raised fill, one-pixel graphite border, primary text, compact radius (4px), and mono text.
- **Focus:** Guide-light outline or amber border in manual-control mode.
- **Error / Disabled:** Failed Red for error text and borders. Disabled states should reduce contrast without dropping below readable text thresholds.

### Navigation
- **Style, typography, default/hover/active states, mobile treatment.** The current app uses a fixed left sidebar with model controls, step control, primary task creation, and accounts access. Preserve the dense vertical rhythm and do not turn it into a marketing-style top nav.

### Task Board
The Kanban board is the signature surface. Columns are equal-width, separated by one-pixel dividers, with compact uppercase headers and semantic title colors. Empty states should teach the workflow more clearly than the current `empty` placeholder when the UI is next polished.

### Live Browser Frame
The live screenshot frame is evidence, not decoration. In manual-control mode, amber border treatment, the `MANUAL CONTROL` badge, and keyboard hint must make direct operator control unmistakable.

## 6. Do's and Don'ts

### Do:
- **Do** preserve the Soft Control Room posture: operational, calm, and readable under task pressure.
- **Do** use Guide Light sparingly for primary action, focus, and completion/report emphasis.
- **Do** keep task lifecycle colors semantic and consistent across dots, labels, banners, and buttons.
- **Do** maintain visible focus states on every control, especially modal fields and manual-control inputs.
- **Do** use empty states and error copy to explain what the operator can do next.

### Don't:
- **Don't** create an intimidating black-box terminal aesthetic; the UI is for AI operators, not only low-level debuggers.
- **Don't** add generic bright SaaS polish, gradient text, glassmorphism, or decorative metrics.
- **Don't** hide important state transitions behind vague labels or color-only cues.
- **Don't** use colored side-stripe borders wider than 1px as accents on cards, callouts, or alerts.
- **Don't** introduce display fonts, large fluid headings, or marketing-page hero patterns inside the dashboard.
