# Project Scaffolding & Multi-Agent Setup

This sub-module guides you through setting up project directories, directory conventions, and configuring a multi-agent workspace.

---

## 1. Directory Structure & Conventions

When using `aloha-python` as a boilerplate for a new project, follow these structural rules:

- **`src/` (Core Application & Tests)**: Place all application-specific code and tests here.
  - **`src/resource/config/`**: HOCON configuration files (e.g. `main.conf`, `deploy-DEV.conf`).
  - **`src/tests/`**: All test files (prefixed with `test_*.py`) and test resources.
- **`doc/` (Documentation & Agent Skills)**: Project Markdown documentation and AI Agent Skills (stored under `doc/skills/`).
- **`notebook/` (Jupyter Notebooks)**: For data analysis, rapid prototyping, and interactive experimentation.
- **`tool/` (CI/CD & Shell Helpers)**: Holds docker compose setups, dockerfiles, and helper scripts.
- **`pkg/` (Library Source - Exclude in Boilerplate Apps)**: This is the core `aloha` package itself. Do not clone/copy the `pkg/` directory when creating a new application project based on this template; your application code should live in `src/`.

---

## 2. Multi-Agent Scaffolding Script

To ensure consistent guidelines, style rules, and skill access across different AI tools (such as Antigravity/Gemini, Claude Code, and GitHub Copilot), run the following scaffolding commands to link config directories:

```bash
# Create scaffolding directories
mkdir -pv .github/workflows doc/skills src/tests tool/cicd

# Create agent config directories and symlink the centralized rules and skills
mkdir -pv doc/skills .agents .claude \
  && touch AGENTS.md \
  && ln -sf AGENTS.md CLAUDE.md \
  && ln -sf ../AGENTS.md .github/copilot-instructions.md \
  && ln -sf ../doc/skills .agents/ \
  && ln -sf ../doc/skills .claude/ \
  && ln -sf ../doc/skills .github/
```

### Integrated Workspace Layout
- **Centralized Rules (`AGENTS.md`)**: The single source of truth for code styling, conventions, and constraints.
- **Centralized Skills (`doc/skills/`)**: Symlinked dynamically to `.agents/skills`, `.claude/skills`, and `.github/skills`. All agents automatically share the same custom instructions.
