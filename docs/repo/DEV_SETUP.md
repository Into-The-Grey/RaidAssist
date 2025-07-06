# Developer Setup Guide

Welcome, developer! This guide helps you get your environment ready for RaidAssist development.

---

## 🖥️ 1. System Requirements

* **Python** 3.8 (required for PySide2 compatibility)
* **Git** (for cloning and version control)
* **OS:** Windows (required for Destiny 2 compatibility; code is cross-platform but only tested on Windows)
* \[Optional] **Visual Studio Code** or your favorite code editor

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

   > **Note:** Hotkey support requires `pyqthotkey>=1.0.4` (now specified in `requirements.txt`).

2. **Developer tools:**

   ```bash
   pip install -r dev-requirements.txt
   ```

3. **Environment variables / API keys:**

   * Copy `.env.example` to `.env` in the project root:

     ```bash
     cp .env.example .env
     ```

   * Fill in your Bungie API key and Client ID in the new `.env` file.

   > **Note:** The app will automatically load variables from `.env` (using `python-dotenv`).
   > **Never commit your real `.env` to the repo.**

---

## 🖼️ 4. Asset Management

* All app icons and images now live in the `/assets/` directory.
* Icons are loaded dynamically using the `get_asset_path()` helper, so asset loading works in dev, EXE, and cross-platform builds.
* If you add new icons or images, place them in `/assets/` and update code to use the helper:

  ```python
  icon_path = get_asset_path('raidassist_icon.png')
  ```

---

## 💾 5. Asset & Cache File Reference

The following files and folders are used or created by RaidAssist at runtime:

| Path                                  | Purpose                | Created by App? | User Clearable? | Notes                               |
| ------------------------------------- | ---------------------- | --------------- | --------------- | ----------------------------------- |
| `assets/raidassist_icon.png`          | UI & tray icon         | No              | No              | Static asset                        |
| `assets/raidassist_icon.ico`          | EXE icon               | No              | No              | Static asset                        |
| `RaidAssist/cache/manifest/`          | Destiny manifest cache | Yes             | Yes             | Fetched from Bungie, can be cleared |
| `RaidAssist/cache/profile.json`       | Profile data cache     | Yes             | Yes             | Refreshed from Bungie API           |
| `RaidAssist/cache/exotics_cache.json` | Exotic lookup cache    | Yes             | Yes             | Built from manifest, can be cleared |
| `RaidAssist/logs/*.log`               | App logs               | Yes             | Yes             | Debug/troubleshooting               |
| `RaidAssist/config/settings.json`     | User/app settings      | Yes             | Yes (planned)   | Written by app/settings UI          |
| `~/.raidassist/session.json`          | OAuth/session tokens   | Yes             | Yes (logout)    | One per user                        |
| `.env`                                | API key/config (local) | No              | Yes             | Never committed or shipped          |
| `.env.example`                        | Env var template       | No              | No              | For devs only                       |

---

## ♻️ 6. Cache & Log Policy

* **Manifest, Profile, and Exotics caches** are created automatically as needed, and can be safely deleted if you encounter corruption or wish to reset app state.
* **Logs** are kept for debugging and troubleshooting; deleting them does not affect app state.
* **Settings** are stored in `RaidAssist/config/settings.json` and updated whenever you change options in the UI.
* **Session tokens** are stored per-user in your home directory, and cleared on logout or by deleting `~/.raidassist/session.json`.

**Note:**
Currently, you must clear cache and logs manually by deleting the relevant files/folders. A one-click “Clear Cache” button is planned for the UI.

---

## 🚀 7. Running the App

```bash
python ui/interface.py
```

*If you add a new main entry-point, update this guide!*

---

## 🧪 8. Running Tests

* Automated tests are currently a placeholder to keep CI passing. Real test coverage is planned as the project evolves.

  ```bash
  pytest
  ```

* Place new tests in the `/tests` folder.

---

## 🎨 9. Code Formatting and Linting

* Format code before PRs:

  ```bash
  black .
  isort .
  mypy .
  ```

* Fix lint errors before pushing.

---

## 🔑 10. Working with Bungie API Keys

* RaidAssist uses a secure, app-owned Bungie API key and OAuth client ID.
* **Do not share your real key in code, docs, or screenshots.**
* The `.env.example` file serves as a template; never commit your filled-out `.env`.

---

## 💡 11. Tips & Troubleshooting

* For manifest or API issues, see `docs/repo/TROUBLESHOOTING.md` (coming soon).
* Check the [README.md](/README.md) and [ROADMAP.md](./ROADMAP.md) for project context.
* If you hit platform-specific UI bugs, please report with your OS details.

---

## 📚 12. More Resources

* [Collaboration Guide](./CONTRIBUTING.md)
* [Code of Conduct](./CODE_OF_CONDUCT.md)
* [CONTRIBUTORS.md](./CONTRIBUTORS.md)

---

Thank you for helping build RaidAssist!
