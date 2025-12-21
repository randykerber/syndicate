# GEMINI.md - Tool-Specific Overrides

## 1. Multi-AI Ecosystem & Gemini's Role

### 1.1 Gemini CLI Specific Constraint
* **Sandboxing:** Respect the sandboxing limitation: never attempt to read or modify files outside the current working directory unless explicitly referenced with `@filename`.
