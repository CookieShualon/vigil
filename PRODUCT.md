# Product

## Register

product

## Users

Vigil is for AI operators who queue, supervise, pause, and recover browser-agent tasks from a local operational dashboard. They need to understand what the agent is doing, intervene when a human step is required, and trust that account cookies, screenshots, reports, and task state are handled transparently.

## Product Purpose

Vigil runs an LLM-driven Playwright browser agent through a web dashboard with task queues, live screenshots, action history, reports, cookie-backed account access, and manual takeover. Success means an operator can launch browser automations, monitor progress, resolve handoffs, and recover failed work without needing to inspect logs or touch the browser process directly.

## Brand Personality

Calm, capable, and transparent. The interface should feel like a steady assistant: clear about state, careful with sensitive account data, and approachable for operators who are managing automation rather than debugging implementation details.

## Anti-references

Avoid intimidating black-box terminal aesthetics, inscrutable agent internals, and generic bright SaaS polish. Do not make routine controls feel dangerous or overly technical, and do not hide important state transitions behind vague status labels.

## Design Principles

Make state legible at a glance: task status, human handoff, failures, and reports should be visually distinct without requiring interpretation.

Keep intervention low-friction: when the operator needs to take the wheel, the UI should make the current browser state and next action obvious.

Expose enough internals to build trust: action history, screenshots, timing, and model choices should be visible, but not dominate the primary workflow.

Treat account access as sensitive: cookie management should communicate local storage, domain scope, and risk clearly.

Favor calm operational density: preserve efficient dashboard scanning while avoiding visual noise, harsh contrast, or unnecessary intimidation.

## Accessibility & Inclusion

Target WCAG AA. Preserve readable contrast for dense dark UI, visible focus states for keyboard use, clear non-color status cues where possible, and reduced-motion alternatives for pulsing or panel transitions.
