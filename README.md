[![CodeQL Advanced](https://github.com/Into-The-Grey/RaidAssist/actions/workflows/codeql.yml/badge.svg)](https://github.com/Into-The-Grey/RaidAssist/actions/workflows/codeql.yml)
[![Python CI](https://github.com/Into-The-Grey/RaidAssist/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Into-The-Grey/RaidAssist/actions/workflows/python-tests.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Open Source](https://badgen.net/badge/open/source/blue?icon=github)](https://github.com/Into-The-Grey/RaidAssist)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-blue?logo=windows)](https://github.com/Into-The-Grey/RaidAssist)

# RaidAssist

**RaidAssist** is a next-generation Destiny 2 desktop companion app and overlay for completionists, hardcore players, and Guardians who never want to alt-tab. It runs on Windows and is fully open source.

---

## ✨ Features (Alpha: v0.2.0)

* **Dashboard Tabs** — See all your Red Border weapons, Catalyst progress, and Exotic collection at a glance. Manifest-driven and auto-cached.
* **Search & Filter** — Quickly search your entire progress and filter by any keyword.
* **Overlay Mode** — One-click, always-on-top overlay for live progress tracking while you play. Move and adjust transparency as you like.
* **Global Hotkey** — Toggle the overlay (Ctrl+Alt+O by default; more customization coming).
* **System Tray Integration** — Minimize to tray, receive pop-up desktop notifications for completion milestones.
* **Tooltips** — Manifest-powered tooltips on every item: archetype, ammo, type, and description.
* **API Tester** — Built-in API test tool for Bungie endpoints, including OAuth token handling and pretty-printed responses.
* **Auto-Refresh & Settings** — Set your own refresh interval; data stays up-to-date automatically.
* **Export** — Save your current progress (JSON/CSV) for backup, theorycrafting, or sharing.
* **Portable by design** — All settings, logs, and caches are stored locally for easy backup and resets.

---

## 🛡️ Bungie API Authentication

RaidAssist uses an official, app-owned Bungie API key (like DIM and Braytech). You never need to register your own developer account or API key.

* On first run, you'll log in with your Bungie account via secure OAuth. A window will pop up for you to approve access to your Destiny 2 profile.
* Only a session token is stored locally; your credentials are never kept or shared.
* All API requests go through the official app key. **No user registration or API key copying required.**
* **OAuth redirect:** RaidAssist uses a secure, self-hosted HTTPS callback on `https://localhost:7777/callback` to handle authentication—no external server required. Self-signed SSL certificates are included for this purpose.

**FAQ:**

* *Is this safe? Will I get banned?* — Yes, it's safe. RaidAssist uses the public, documented API flows Bungie allows.
* *Is my data private?* — Yes. Everything is local-only unless you choose to export/share it.
* *Why do I see a browser SSL warning?* — The included `localhost.pem` cert is self-signed, so your browser may show a warning when authenticating. This is normal and safe for local use.

#### Note on SSL Certificates

This project includes `localhost.pem` and `localhost-key.pem` for local OAuth authentication with Bungie. These are self-signed and only used for development/testing. End users do **not** need to manage certificates or secrets.

---

## 🚧 Project Status & Alpha Notice

**Alpha Release v0.2.0** — For early adopters, testers, and feedback. Stable core, but you may encounter bugs or edge cases.

* Self-contained Python app, with EXE installer and auto-authentication (no manual .env required for users!)
* Full roadmap and premium features (below) are on the way.

---

## 🔥 Roadmap: Upcoming Features

See [ROADMAP.md](/docs/repo/ROADMAP.md) for details. Highlights include:

* Multi-account/profile support
* Complete raid, dungeon, and activity tracking
* Custom overlay widgets & layouts
* Weekly milestones and vendor rotation
* Cloud sync and mobile/web dashboard
* Discord/social integrations
* Loadout management, recommendations, and builds
* Enhanced stats, milestone popups, and more

---

## 🛠️ Installation & Quick Start

1. **Requirements:**

   * Python 3.8+ (required for PySide2 compatibility)
   * Windows (required for Destiny 2 compatibility)
   * See [requirements.txt](/requirements.txt) for dependencies (PySide2, requests, pyqthotkey)

2. **Install:**

   ```bash
   pip install -r requirements.txt
   ```

3. **First run:**

   ```bash
   python ui/interface.py
   ```

   *(Follow the prompt to log in with Bungie; no extra setup required. EXE releases available as artifacts.)*

> **Installer/EXE included in releases and Actions artifacts.**

---

## 🧑‍💻 Developer Info & Contributing

* See [Developer Setup Guide](./DEVELOPER_SETUP.md) for full environment and local build steps.
* [Collaboration Guide](./CONTRIBUTING.md) for PR/branch guidelines and community expectations.
* [Code of Conduct](./CODE_OF_CONDUCT.md) for behavior and inclusion.

All app logic, cache, and logs are stored in `/RaidAssist/` folders—see [Developer Guide](./DEVELOPER_SETUP.md) for asset/cache structure.

---

## 📝 License

**GPL v3.0** — See [LICENSE](LICENSE) for full terms and header requirements.
Free, open-source, and copyleft: you can use, copy, and fork, but must preserve license and attribution.

---

## 📷 Screenshots

![Dashboard Screenshot](docs/images/dashboard.png)
![Overlay Demo GIF](docs/images/overlay-demo.gif)

---

**Questions, bugs, or feature ideas?**

* Open an [issue](https://github.com/Into-The-Grey/RaidAssist/issues)
* PRs and suggestions welcome!
