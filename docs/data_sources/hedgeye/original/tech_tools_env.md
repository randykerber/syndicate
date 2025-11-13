# Project Environment & Behavior

This document captures important setup conventions, tools, and hidden behaviors that affect how the project runs — especially those **not obvious** from just reading `pyproject.toml` or code.

---

## 🐍 Python Environment

* **Toolchain**: Python 3.13, managed with [`uv`](https://github.com/astral-sh/uv)
* **Virtual environment**: Located in `.venv/`, not committed to git.
* `.python-version` file exists with content `3.13` — used by `uv` and editors like PyCharm or Cursor to auto-select the interpreter version.

---

## 📦 Project & Dependency Management

* **Tool**: [`uv`](https://github.com/astral-sh/uv)
* **Dependencies declared in**: `pyproject.toml`
* **Lockfile**: `uv.lock`
* **Workflow**:

  * Add: `uv add <package>`
  * Remove: `uv remove <package>`
  * Snapshot: `uv pip freeze > requirements.txt` (optional, for compatibility with tools expecting `requirements.txt`)

---

## 🌱 direnv Auto-Environment Activation

* **Tool**: [`direnv`](https://direnv.net/)

* **Purpose**: Automatically loads `.envrc` when you `cd` into the project directory.

* **Shell integration** (required for auto-loading to work):

  Add to `~/.bashrc`:

  ```bash
  # Enable automatic loading of .envrc for direnv
  eval "$(direnv hook bash)"
  ```

* **Common contents of `.envrc`**:

  ```bash
  layout python
  export PYTHONPATH=src
  ```

  (You may also include secrets or project-specific env vars.)

* **.envrc must be allowed once per machine**:

  ```bash
  direnv allow
  ```

---

## 🔐 Secrets & Environment Variables

* **Optional `.env` file**:

  * Used for setting local env vars without polluting global shell config
  * Can be loaded via `dotenv` in Python scripts
  * Not committed to git (included in `.gitignore`)

---

## 📂 Project Layout Highlights

* `src/`: all Python source code
* `scripts/`: utilities and CLI entry points
* `data/`: raw and processed data, ignored from git
* `docs/`: documentation like this one

---

## 🧼 Hidden or Non-Obvious Gotchas

* `PYTHONPATH=src` must be set (manually or via `.envrc`) to allow relative imports from `src/python/`
* Not setting `eval "$(direnv hook bash)"` in `.bashrc` means `.envrc` won’t load, even if present and allowed.
* Tools like `uv` work without `requirements.txt`, but some third-party tools expect it — so it can be generated if needed.

---


