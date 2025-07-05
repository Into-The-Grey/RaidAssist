# Collaboration Guide

Welcome to **RaidAssist** — we’re thrilled to have you on board!

This guide outlines how to contribute effectively and collaborate with others in the project.

---

## 🚀 Getting Started

1. **Read the README**
   Start with [`README.md`](/README.md) to understand the project’s purpose, core features, and architecture.

2. **Check the Roadmap**
   See what’s planned and what’s in progress in [`ROADMAP.md`](./ROADMAP.md).
   You can request assignment to an open task, or propose a new one via an issue or PR.

3. **Development Setup**

   * Clone your fork locally and set the upstream remote.
   * Install dependencies for both the app and development:

     ```bash
     pip install -r requirements.txt
     pip install -r dev-requirements.txt
     ```

   * See [`DEV_SETUP.md`](./DEV_SETUP.md) (coming soon) for full details.

---

## 🛠️ How to Contribute

1. **Create a Feature Branch**
   Use descriptive names like `feature/overlay-toggle` or `bugfix/exotic-status-crash`.

2. **Write Clean, Modular Code**
   Follow existing conventions, add docstrings, and comment for clarity.

3. **Testing**
   If your contribution includes backend logic, add/maintain tests using `pytest`.
   Run all tests before submitting a PR.

4. **Submit a Pull Request (PR)**

   * Clearly explain your changes and reasoning.
   * Reference related issues (e.g., `Fixes #42`).
   * Tag reviewers/maintainers as needed.

---

## 📐 Code Style

* Use 4-space indentation (Python)
* Stick to `snake_case` for variables and functions
* Use docstrings for all classes and public methods
* Lines under 100 characters preferred
* Run code formatters before submitting:

  ```bash
  black .
  isort .
  mypy .
  ```

---

## 🧪 Testing

* All logic should be covered by tests where possible.
* We use **pytest**; see existing tests as examples.
* Run `pytest` before submitting PRs.

---

## 🤝 Community Expectations

* Review others’ PRs when you can
* Be constructive and supportive in code reviews and issues
* Follow our [Code of Conduct](./CODE_OF_CONDUCT.md)

---

## 🙏 Acknowledgement

By contributing, you agree to be listed in [`CONTRIBUTORS.md`](./CONTRIBUTORS.md) unless you request otherwise.

Thanks for helping make RaidAssist better for the Destiny 2 community!
