# Developer Setup Guide

Welcome, developer! This guide helps you get your environment ready for RaidAssist development.

---

## 🖥️ 1. System Requirements

* Python 3.8 or higher (recommended: 3.10–3.12)
* Git (for cloning and version control)
* OS: Windows, macOS, or Linux

---

## ⚡ 2. Clone the Repository

```bash
git clone https://github.com/yourusername/raidassist.git
cd raidassist
```

---

## 📦 3. Install Dependencies

1. **User/app dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Developer tools:**

   ```bash
   pip install -r dev-requirements.txt
   ```

---

## 🛠️ 4. Running the App

```bash
python ui/interface.py
```

*If you add a new main entry-point, update this guide!*

---

## 🧪 5. Running Tests

* We use `pytest` for all tests:

  ```bash
  pytest
  ```

* Place new tests in the `/tests` folder.

---

## 🎨 6. Code Formatting and Linting

* Format code before PRs:

  ```bash
  black .
  isort .
  mypy .
  ```

* Fix lint errors before pushing.

---

## 💡 7. Tips & Troubleshooting

* For manifest or API issues, see `docs/repo/TROUBLESHOOTING.md` (coming soon).
* Check the [README.md](/README.md) and [ROADMAP.md](./ROADMAP.md) for project context.
* If you hit platform-specific UI bugs, please report with your OS details.

---

## 📚 8. More Resources

* [Collaboration Guide](./CONTRIBUTING.md)
* [Code of Conduct](./CODE_OF_CONDUCT.md)
* [CONTRIBUTORS.md](./CONTRIBUTORS.md)

---

Thank you for helping build RaidAssist!
