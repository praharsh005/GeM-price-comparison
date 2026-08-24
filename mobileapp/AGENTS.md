# agent.md — device & system change policy

> Place this file at the root of your repository. Most agentic coding tools (OpenCode, Antigravity, and others) auto-read a root-level `agent.md` / `AGENTS.md` each session — check your tool's docs for the exact filename it looks for and duplicate/rename if needed. This file works alongside `master-agent-prompt.md`; if the two ever disagree on permission handling, **this file wins**.

---

## The core rule

Before performing any action that changes something **outside this project folder** — the operating system, globally installed software, apps, or device settings — the agent must **stop and ask the user a direct yes/no question**, then wait for an explicit reply. No such action may be taken silently, bundled inside a larger step, or described only after the fact.

---

## Always requires yes/no confirmation first

- Installing any application, package, or tool **outside this project's own virtual environment / `node_modules`** — e.g. `apt install`, `brew install`, `choco install`, `winget install`, global `npm install -g`, global `pip install`
- Downloading, opening, or running any installer or package file — `.apk`, `.exe`, `.msi`, `.dmg`, `.deb`, shell installer scripts, etc.
- Any command requiring `sudo`, administrator, or root privileges
- Changing OS-level settings: system-wide PATH or environment variables, firewall/network settings, system services, scheduled tasks
- Installing or modifying browser extensions, browser settings, or default applications
- Deleting or modifying any file or folder **outside this project's working directory**
- Changing Docker Desktop, WSL, virtualization, or other host-level settings
- Any action the agent cannot cleanly undo

## Does not need a prompt every time

- Installing packages already declared in `requirements.txt` / `package.json` into the project's own venv or `node_modules`
- Running project scripts, tests, migrations, and `docker-compose` commands that only touch containers defined in this repo
- Creating, editing, or deleting files inside the project folder

**Adding a brand-new dependency** to `requirements.txt`/`package.json` should be flagged once when it's first introduced (so the user knows a new package is entering the project), but doesn't need re-asking every time it's reinstalled afterward.

---

## Exactly how to ask

When permission is required, stop and ask in this format:

```
PERMISSION NEEDED
Action: <exactly what will be run / installed / changed>
Why: <why it's needed for the current phase>
Scope: <project-only / device-wide / requires admin>
Reversible: <yes — how / no — why not>

Proceed? (yes/no)
```

Wait for an explicit **"yes"** or **"y"** before continuing. Anything else — "no," silence, "maybe," or an unrelated reply — is treated as **no**: do not proceed. Instead, explain the alternative (e.g. skip that dependency, use a project-scoped package instead of a system one, or ask the user to install it manually).

## If the user says no

Do not repeat the same request without being asked to. Look for a project-scoped alternative first (e.g. a pip package inside the venv instead of a system package) and propose that instead of the device-level change.

## Logging (optional, recommended for your project report)

Keep a `PERMISSIONS_LOG.md` in the project root, appending one line per request: date, action requested, user's answer. This doubles as a nice appendix showing controlled, permission-gated agent behavior when you write up the project.

---

## Context usage & response style

- Keep context usage minimal: don't re-read files that haven't changed, don't paste full file contents into chat when a small diff or snippet will do, avoid redundant tool calls.
- Default responses to the user should be **short and to the point** — a brief status update (what changed, test pass/fail, what's next), not a restated plan or long narrative.
- Exception: if the user asks a question, asks for an explanation, or explicitly asks for more detail, answer fully — don't compress an answer someone actually asked for.
- Skip filler ("Great question!", "Let me think about this," "I have successfully completed..."). State the outcome directly.

---

## Context & response style

- Default to **minimal context usage and concise, to-the-point responses**. Status updates should state what was done and what's next — no restating the whole plan, no narrating obvious steps, no filler.
- Exception: if the user asks a question, something is ambiguous, or a permission request/error needs explaining, give the full context needed for the user to actually understand and decide. Brevity should never come at the cost of clarity when it matters.

---

## Planning mode

Applies whenever a new phase or feature is being scoped, before any code is written.

- Always ask clarifying questions first. Never assume design, tech stack, or features that aren't already specified in `master-agent-prompt.md`.
- Use deep-dive sub-agents (if the tool supports sub-agent delegation) to research open questions before proposing a plan.
- Use deep-dive sub-agents to review different aspects of the plan (e.g. one checking the DB schema impact, one checking the API contract) before presenting it to the user.

## Change / edit mode

- Prefer delegating implementation to sub-agents over writing every line yourself, when the tool supports it.
- Identify parts of the plan that can be implemented in parallel and hand those to separate sub-agents.
- When using sub-agents, act as coordinator only: assign work, review output, integrate it — don't duplicate their work yourself.
- Match model tier to task difficulty: the strongest available model for complex work (core backend logic, the matching algorithm, tricky scraping edge cases), a lighter/mid-tier model for simpler work (documentation, boilerplate, formatting).
- After completing any feature, large or small, run lint, type-check, and build commands to verify code quality before considering it done.

## Database schema changes

> Adapted for this project's actual stack — SQLAlchemy + Alembic, not Drizzle (Drizzle is a JS/TS ORM and doesn't apply to a Python/FastAPI backend). If you're pasting this file into a different project that does use Drizzle, swap this section back.

- Whenever the database schema changes, ALWAYS generate a migration with `alembic revision --autogenerate -m "<description>"` and apply it with `alembic upgrade head`.
- NEVER modify the schema directly — no `Base.metadata.create_all()` against a running database, no manual `ALTER TABLE` outside a migration file. Every schema change must go through a tracked migration.

## Testing

- Use whatever testing tools are already available in the project (pytest for the backend, React Testing Library/Vitest for the frontend) to verify changes.
- Never assume a change simply works — always test it.
- If no testing tooling exists yet for a given piece of code, ask the user whether to skip testing for it rather than silently skipping it.

## UI design

- Always follow the project's design system when creating or reviewing components or pages.
- Design system reference: `DESIGN.md`.

> Note: this project doesn't have a `DESIGN.md` yet. Until one exists, agents should ask the user for style direction rather than inventing one. Say the word and I can draft a starter `DESIGN.md` (colors, type scale, spacing, component conventions) to go with this.
