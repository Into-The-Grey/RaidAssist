[![CodeQL Advanced](https://github.com/Into-The-Grey/RaidAssist/actions/workflows/codeql.yml/badge.svg)](https://github.com/Into-The-Grey/RaidAssist/actions/workflows/codeql.yml)
[![Python CI](https://github.com/Into-The-Grey/RaidAssist/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Into-The-Grey/RaidAssist/actions/workflows/python-tests.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Open Source](https://badgen.net/badge/open/source/blue?icon=github)](https://github.com/Into-The-Grey/RaidAssist)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-blue?logo=windows)](https://github.com/Into-The-Grey/RaidAssist)

# RaidAssist

**RaidAssist** is a next-generation Destiny 2 desktop companion app and overlay for completionists, hardcore players, and Guardians who never want to alt-tab. It runs on Windows and is fully open source.

---

## ✨ Features (Alpha: v0.3.0)

* **Plug-and-play OAuth & Secure Auth:** One-click first-run authentication—browser auto-launch, secure Bungie login, automatic local HTTPS callback (`https://localhost:7777/callback`). No user config or secrets required. Self-signed SSL certs included for easy OAuth.
* **Dashboard Tabs** — See all your Red Border weapons, Catalyst progress, and Exotic collection in real time. Manifest-driven and auto-cached.
* **Search & Filter** — Instantly filter by any name, archetype, or type.
* **Overlay Mode** — Always-on-top, draggable, resizable overlay for in-game use. Transparency and styling options included.
* **Global Hotkey** — Toggle overlay instantly (Ctrl+Alt+O by default).
* **System Tray Integration** — Minimize to tray, get pop-up desktop notifications for completion milestones.
* **Tooltips** — Manifest-powered tooltips: archetype, ammo, type, description, and source.
* **API Tester** — Run any Bungie API endpoint, with OAuth and pretty formatting.
* **Auto-Refresh & Settings** — User-settable refresh interval, background updates, easy status view.
* **Export** — Save your progress (JSON/CSV) for backup, analytics, or sharing.
* **Portable by design** — All app state, logs, and cache in `/RaidAssist`—easy to backup, wipe, or reset.

---

## 🛡️ Bungie API Authentication

RaidAssist uses OAuth 2.0 PKCE (Proof Key for Code Exchange) for secure authentication with the Bungie API.

### 🚀 For End Users

* **Download the latest release** - OAuth credentials are pre-configured
* **First run:** App opens your browser for Bungie login
* **Automatic:** Secure token exchange happens automatically
* **Safe:** No API keys or secrets to manage

### 🔧 For Developers

OAuth setup is required for development:

1. **Get Bungie API credentials** at [bungie.net/Application](https://www.bungie.net/en/Application)
2. **Copy environment template:** `cp .env.example .env`
3. **Fill in your credentials** in the `.env` file
4. **Verify setup:** `python verify_oauth_setup.py`

See [docs/OAUTH_SETUP.md](docs/OAUTH_SETUP.md) for detailed setup instructions.

#### Security Notes

* OAuth flow uses PKCE - no client secrets required
* Local HTTPS server with self-signed certificates for callback
* Only session tokens stored locally, never your credentials
* All authentication handled by Bungie's official OAuth system

---

## 🚧 Status: v0.3.0-alpha (July 2025)

* **First Windows EXE with zero-config OAuth onboarding**
* **All logs, cache, and settings are portable and easy to reset**
* **EXE packaging, UI, and performance improvements in progress**
* **Bugs and feedback welcome!**

---

## 🔥 Roadmap: Next Features

See [ROADMAP.md](/docs/repo/ROADMAP.md) for details. Highlights include:

* Multi-account/profile support
* Raid/dungeon/activity tracking
* Custom overlay widgets/layouts
* Vendor and milestone reminders
* Discord/social integration
* Loadout/builds management
* UI/UX and accessibility upgrades

---

## 🛠️ Installation & Quick Start

1. **Requirements:**

   * Windows (for Destiny 2 compatibility)
   * Python 3.8+ (for dev builds only)
   * Download the EXE from Releases or Actions for plug-and-play use
   * [requirements.txt](/requirements.txt) lists Python dependencies

2. **Install:**

   ```bash
   pip install -r requirements.txt
   ```

3. **First run:**

   ```bash
   python ui/interface.py
   ```

   *(App opens browser for Bungie login—no config or .env needed! EXE is in Releases and Actions.)*

> **Latest EXE is downloadable in Releases and Actions Artifacts.**

---

## 🧑‍💻 Developer Info & Contributing

* [Developer Setup Guide](./DEVELOPER_SETUP.md)
* [Collaboration Guide](./CONTRIBUTING.md)
* [Code of Conduct](./CODE_OF_CONDUCT.md)

All app state, cache, logs, and settings are stored in `/RaidAssist` (see dev docs for structure).

---

## 📝 License

**GPL v3.0** — See [LICENSE](LICENSE) for full terms. Fork, build, or modify, but keep license and credit.

---

## 📷 Screenshots

![Dashboard Screenshot](docs/images/dashboard.png)
![Overlay Demo GIF](docs/images/overlay-demo.gif)

---

**Questions, bugs, or feature ideas?**

* Open an [issue](https://github.com/Into-The-Grey/RaidAssist/issues)
* PRs and suggestions are always welcome!
