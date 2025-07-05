# RaidAssist

**RaidAssist** is a next-generation Destiny 2 desktop companion app and overlay for dedicated players and completionists.
Built for PC, RaidAssist puts your meta progress, catalysts, exotics, and crafting at your fingertips—**without alt-tabbing**.

---

## ✨ Features (Alpha)

* **Dashboard Tabs:** Instantly see all your Red Border weapons, Catalyst progress, and Exotic collection in a clean interface.
* **Search & Filter:** Quickly find any item across your collection.
* **Overlay Mode:** One-click, always-on-top overlay for live progress tracking while you play. Move and adjust transparency as you like.
* **Global Hotkey:** Toggle the overlay in and out with Ctrl+Alt+O (configurable in future).
* **System Tray Integration:** Minimize to tray, with menu and desktop notifications for milestones (pattern/catalyst/exotic completion).
* **Tooltips:** Hover any item for manifest-backed details—archetype, ammo, description, and more.
* **API Tester:** Run Bungie API calls right from the app for power users and debugging.
* **Auto-Refresh & Settings:** Keep data up-to-date automatically, with refresh interval control.
* **Data Export:** Export your current progress (JSON/CSV) for analysis or sharing.

---

## 🛡️ Bungie API Authentication

RaidAssist uses an official, app-owned Bungie API key to connect securely to Bungie.net—just like DIM, Braytech, and other trusted Destiny 2 apps.  
**You never need to register your own API key or developer account.**

* On first run, RaidAssist will ask you to log in with your Bungie account via OAuth.
* Your credentials are never stored; only a temporary session token is saved (locally, never uploaded).
* All communication is handled via the app's API key, so setup is instant and hassle-free.

**FAQ:**  

* "Will this get me banned?" — No. Using the official Bungie API and OAuth is fully supported, just like Destiny Item Manager and Braytech.
* "Is my data private?" — Yes. Only your own OAuth token is stored locally, and never shared.

---

## 🚧 Status: v0.1.0-alpha

This is an **alpha release** for testers, early adopters, and feedback.
Features are stable, but bugs and quirks may exist.
Major expansions (see below) are in progress.

---

## 🔥 Roadmap / Upcoming Features

Planned and premium features include:

* **Multi-account support**
* **Full raid, dungeon, and activity tracking**
* **Custom overlay widgets & layout**
* **Weekly milestones and vendor rotation**
* **Cloud sync & mobile/web dashboard**
* **Discord/social integration**
* **Loadout management & recommendations**
* **More notifications & advanced stats**

See the [Roadmap](/docs/repo/ROADMAP.md) for details.

---

## 🛠️ How to Use / Install

1. **Requirements:**

   * Python 3.8+
   * See [requirements.txt](/requirements.txt) for dependencies (`PySide2`, `requests`, `pyqt-hotkey`).

2. **Running the App:**

   ```bash
   pip install -r requirements.txt
   python ui/interface.py
   ```

   *(Installer/exe coming soon)*

---

## 🤝 How to Contribute

Check out our [Collaboration Guide](/docs/repo/CONTRIBUTING.md) for dev setup, code standards, and submitting PRs.

---

## 💬 Code of Conduct

We are committed to a welcoming, inclusive community.
See our [Code of Conduct](/docs/repo/CODE_OF_CONDUCT.md).

---

## 📝 License

This project is licensed under the Apache License 2.0.
See [LICENSE](/docs/repo/LICENSE) for details.

---

## Screenshots

![Dashboard Screenshot](docs/images/dashboard.png)
![Overlay Demo GIF](docs/images/overlay-demo.gif)

---

**Have feedback, bug reports, or feature requests?**
Open an issue or join our community—every suggestion helps shape RaidAssist!
