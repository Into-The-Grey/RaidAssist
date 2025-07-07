# Changelog

## [v0.1.0-alpha] — 2025-07-07

### Major Features

- **Multi-Tab Dashboard:**  
  - Real-time, searchable tabs for Red Border weapons, Catalyst progress, and Exotic collection.
  - Manifest-backed tooltips for all items, including name, archetype, ammo, and detailed description.

- **Overlay Mode:**  
  - Click-to-toggle, always-on-top overlay for live progress tracking in-game.
  - Adjustable transparency and drag-to-move overlay window.
  - Global hotkey toggle (`Ctrl+Alt+O`) using `pyqthotkey` (Windows-only for now).

- **System Tray Integration:**  
  - Minimize to tray support, with custom app icon.
  - Desktop notifications for milestone events (red border patterns, catalyst completions, new exotics).

- **API Tester:**  
  - Built-in dialog to send and view arbitrary Bungie API requests.
  - Supports authenticated endpoints with session-based OAuth token.

- **Settings & Auto-Refresh:**  
  - User-editable refresh interval.
  - Data auto-refreshes in the background, with status updates in the UI.

- **Data Export:**  
  - Export tab data (Red Borders, Catalysts, Exotics) to JSON or CSV for analysis or sharing.

### Infrastructure / Developer Improvements

- **Cross-platform Project Structure:**  
  - All app state, cache, logs, and configs are created in the `/RaidAssist` folder for clarity and cleanup.
  - Asset path resolution works in both development and PyInstaller builds.

- **Absolute Path Handling:**  
  - All modules use `get_project_root()` and `os.path.join()` to avoid import/path errors on Windows.

- **API & Manifest Integration:**  
  - Manifest data cached locally for speed and offline use.
  - Exotics detection and tracking is 100% manifest-driven—no hardcoded lists.

- **Logging:**  
  - Centralized logging in `/RaidAssist/logs` for all API, manifest, and interface activity.
  - Errors and warnings are clearly surfaced to users and logs.

- **Testing:**  
  - Core functions (manifest, exotics cache, profile parsing) have basic automated tests in `/tests`.

- **CI/CD:**  
  - CodeQL analysis, Dependabot, labeler, and greeting bots enabled for repo automation and security.

### Other

- **Environment Variable Support:**  
  - `.env` config supported (via `python-dotenv` if installed), with `.env.example` template.
  - Fallback to system environment variables if `.env` not present.

- **App Icon and Assets:**  
  - Flat, vector-based icons for Windows EXE and system tray included.
  - All assets bundled via PyInstaller spec for easy distribution.

### Known Limitations

- First-time setup requires a Bungie API key and OAuth client configuration.
- No installer/EXE yet; Windows packaging is in progress.
- UI is desktop-only (PySide2). In-game overlay is an always-on-top window, not a true game hook.
- Test suite is minimal—full coverage coming in later versions.

---

**This is an alpha release. Expect rapid iteration and breaking changes as we prepare for the first public beta.  
Feedback, bug reports, and feature requests are welcome!**


## [v0.1.0-alpha] — 2025-07-05

- First fully-bundled Windows build (PyInstaller): no Python or pip required on user systems.
- Added support for a shared, app-owned Bungie API key for all user requests (no user API key setup needed, follows best practice like DIM/Braytech).
- Updated docs: explained authentication and user privacy for transparency.

## [v0.1.0-alpha] — 2025-07-04

- Initial public alpha release!
- Core dashboard, overlay, notifications, tray integration, and export features.
- MVP features listed in README.
- Known issues:
  - No installer yet; run via Python.
  - Some Bungie manifest data may be missing details.
  - No multi-account support.
