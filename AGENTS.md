<!-- BEGIN AGENTPREP MANAGED BLOCK -->
## AgentPrep AI Operating Rules

Use of AI in conjunction with this repository is governed by
[AgentPrep](https://github.com/provenant-dev/agentprep).

As an AI, you will need to know how to identify yourself to the
agentprep tool. Canonical ai_agent_name values are:

    `claude`, `codex`, `copilot`, `cursor`, `gemini`, or `openclaw`

If you are one of these tools, great; use the appropriate ai_agent_name
with agentprep. If you are an AI but your name is not in this
list, stop immediately and tell the user to manually edit this AGENTS.md
file so you recognize your name in the list above.

Once you can name yourself canonically, **before starting any task that
will involve a git commit**, run:

```bash
agentprep verify --agent <ai_agent_name>   # or: export AGENTPREP_AGENT=<ai_agent_name>
```

If verification fails with `verify failed: missing .ai-safety-check.*`, **stop
and tell the user before writing any files**. A git pre-commit hook (committed to
`.githooks/pre-commit` and installed automatically to `.git/hooks/pre-commit` by
`agentprep init` and `agentprep certify`) will block every commit you attempt until
the user runs `agentprep certify --agent <name>` to attest a correct config. Do not
attempt the task until the user confirms they've certified. Then cache the lease timestamp produced by `agentprep verify` once
verification succeeds; you do not need to re-verify within the same session.

The following operations are reserved for humans. The `.agent-bin` shims
installed in this repository will block them if an agent attempts them:

- `git push` to protected branches (defaults: `dev`, `main`, `master` — `dev` is included because it is a shared integration branch, not a personal feature branch) and destructive push modes (`--delete`, `--all`, `--mirror`)
- `gh pr merge` — merging a pull request
- `gh repo delete` — deleting the repository

Creating, viewing, and updating pull requests is permitted (`gh pr create`,
`gh pr edit`), as is pushing feature branches for PR workflows.

Place `.agent-bin` at the front of PATH in agent shells so the shims are active:

```bash
export PATH="$PWD/.agent-bin:$PATH"
```

The `.agent-bin/git` and `.agent-bin/gh` shims are thin pass-throughs: they
make a quick allow/block decision and then `exec` the real binary with the
original arguments. They do not scan the working tree, read project files, or
inspect git history. If a `git` or `gh` invocation is unexpectedly slow, the
shim is not the cause — diagnose the underlying tool. In particular, slow
`git add -A` usually means a multi-thousand-file directory (e.g. `.venv/`,
`node_modules/`, `build/`) is not covered by `.gitignore`; fix `.gitignore`
or stage explicit paths instead. Run `agentprep doctor` to surface common
gitignore-hygiene problems.
## Testing Protocol

This repository has an established test suite. Follow strict TDD:
1. Write one or more failing tests that capture each requirement (including
   both happy paths and its edge cases/unhappy paths) before implementing.
2. Implement until all tests pass.
3. Never commit unless all tests pass. Coverage of any code you touch
   must not decrease.

## CI and Documentation

This repo has no CI workflows. Until it does, any time you make code
changes to the user, propose an appropriate set of GitHub actions (e.g.,
`.github/workflows/ci.yml`) that builds and runs tests on every push and
pull request. Propose to remove this instruction from AGENTS.md on the
same commit.

When writing or modifying GitHub Actions workflows, always use the latest
stable release of each action. Avoid versions pinned to Node.js 16 or
Node.js 20 (both deprecated by GitHub). In 2026, this meant to prefer Node.js
24-compatible versions, but the standard may evolve over time. Check the GitHub
Marketplace for each action's current release.

## Origin Platform Context

This codebase is part of the Origin platform ecosystem. Other origin-related
repositories likely exist as siblings in the parent directory (e.g.,
`../origin-auth-lib`, `../origin-common-lib`, `../origin-deployment`); they
definitely exist as sibling repos under https://github.com/provenant-dev/.
Each sibling repo typically has `README.md` and a `docs/` folder containing
design docs with important metadata. This knowledge is available to you and
you should consult it (making sure the local code is current and on its
default branch) if you need broader context than the current repo.

The `../origin-platform/` sibling is the platform-wide knowledge base. Its
`docs/origin-platform/` directory contains platform-wide architecture guides, API
conventions, security requirements, deployment specifications, and cross-cutting
platform decisions. Before making changes that could touch platform conventions —
authentication, URL design, error formats, data models, Kafka topics, deployment
patterns, or testing strategy — consult the relevant doc in
`../origin-platform/docs/origin-platform/`. Start with
`general-origin-characteristics.md`; follow links there to more specific guides.

When a proposed change has platform-wide implications, check whether relevant
sibling repos' `docs/` folders offer useful constraints before proceeding.

The `../origin-platform/prompts/` directory contains reusable AI reviewer prompts
designed for Origin platform codebases. They create named and dated reports in a
/reviews folder in this repo and constitute prioritized next steps or action items
for improving the code. Consider recommending one or more of these to the user after
significant changes, before a release, or during onboarding:

- **`platform-architect.md`** — Reviews alignment with platform-wide API, auth,
  data, and communication conventions; flags drift that creates integration problems.
- **`security-hawk.md`** — Adversarial security review: auth bypasses, authorization
  holes, injection paths, replay attacks, and secret exposure.
- **`compliance-auditor.md`** — SOC-2 / regulatory readiness: audit trails, access
  controls, evidence of consistently operating controls.
- **`maintainability-expert.md`** — Identifies intent boundaries, missing rationale,
  and patterns likely to be incorrectly "fixed" by future developers or AI agents.
- **`testability-hawk.md`** — Finds structural testability gaps across all test layers;
  surfaces classes of missing tests rather than individual cases.
- **`devops-engineer.md`** — Deployment, CI/CD, Docker/Helm correctness, Kubernetes
  health probes, and local development ergonomics.
- **`ux-guru.md`** — UX and frontend architecture review (skip for pure backend repos).
- **`generate-arch-doc.md`** — Generates or refreshes `docs/architecture.md`.

To use a prompt, open the file in your AI tool's context and run it against the
current workspace. Periodic runs of `platform-architect.md` and `security-hawk.md`
are especially recommended as the platform evolves. Once the action items in a report
have all been triaged, they should be deleted (but remain in git history to show
what was done).

If this repo does not have a docs/architecture.md file, always propose creating one
using `generate-arch-doc.md`.

## Methodology

This repo should have a file called `this.i` at the root. It records the *why* behind every design
decision as a tree of `goal:`, `decision:`, `constraint:`, and `tension:` nodes. It is the
most important file in the repo for understanding why things are built the way they are. The
file is YAML and should be parsed as YAML; do not pattern-match indentation.

Adopt this stance toward it:

1. **The intent tree describes a destination, not just current state.** Nodes may describe
   completed stages or planned futures; read stage-status fields to distinguish them.
2. **Tension resolutions are binding.** Implement consistently with recorded resolutions.
   Do not re-open them or silently resolve them differently.
3. **`why` fields are primary evidence.** When making any decision touching a node, the `why`
   is the most important thing to read.
4. **`deviation:` nodes are the complete list of approved gaps.** Discovery is by node type
   (every `deviation:` node in `this.i`), not by a numbered list; any gap not represented by a
   `deviation:` node is a defect requiring Daniel's approval before it can be accepted.
5. **Before making any decision that meets the trigger criteria, record it in `this.i` first.**
   The concrete trigger list is in `docs/methodology.md §3` (vendor that file into this repo
   first if it isn't present yet — see below).

For the full context of what `.i` files are, the intellectual lineage of this system, what makes
a `why` field adequate, and what triggers a required `this.i` update, read `docs/methodology.md`
This repo is meant to carry its own vendored copy of that file: if `docs/methodology.md` is not
present, copy it in from `../origin-platform/docs`, commit it, and then read it. The checked-in
copy is only a starting point — adapt it to this repo as the methodology evolves here; it is
deliberately not kept in sync with the origin-platform original.

DO NOT modify code here without understanding the methodology. You should have a clear idea of
what a "speculative interview" is, how it's done, and where its output is recorded; what a "tension"
is in intent; how "marks" work; how we use Fowler's _Refactoring_ discipline to continually improve
DRY, encapsulation, and names in code.

If you don't see a `this.i` in this repo's root, you must create one. To understand how, study one in
a sibling repo (`../origin-sip-policy-admin` has an excellent example). Notice how it relates to code
but explains things that are often missing from the code. Then use sources like the code, `README.md`,
and `docs/*.md` (possibly creating `docs/architecture.md` using the `generate-arch-doc.md` prompt if
needed) to form theories about design decisions in this codebase. Then interview the user to confirm
or disprove your theories, and write a starter `this.i` when you're done. (If the codebase is empty,
just ask the user about their intentions for it, and begin building from there.)
<!-- END AGENTPREP MANAGED BLOCK -->

<!-- >>> tick stanza >>> (managed by `tick init`) -->

## Task tracking: `tick`

This repo tracks tasks, tech debt, and ideas in a local [`tick`](https://github.com/dhh1128/tick)
ledger (an orphan `tick` branch; the `tick` CLI is the interface). Reads are plain
files — do **not** use an external API for task tracking.

- **First, if a `tick` command says the repo isn't initialized**, run `tick init`
  once to connect this clone to the ledger — it adopts the existing remote ledger
  if a colleague already set one up, or creates a new one otherwise.
- **A tick mark is the sigil `~` immediately followed by a digit-first 4-char
  base32 id** (the id part looks like `4mz3`, so the full mark is that id with a
  leading `~`). It pins a tick to a code location.
- **Before editing a file**, grep it for marks and read what they reference:
  `rg '~[2-7][a-z2-7]{3}\b' <file>` then `tick show <id>`. A mark means recorded
  context exists for that spot — read it first.
- **Search** existing ticks with `tick grep <text>`; **list** with `tick ls`.
- **Capture** new work with `tick add "<title>"` and place the printed mark
  (`~` + the new id) at the relevant code spot.
- When your change **resolves** a tick, run `tick off <id>` and **delete the
  mark(s)** it reports still in the code.

<!-- <<< tick stanza <<< -->
