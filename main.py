# RaidAssist — Destiny 2 Progression Tracker and Overlay
# Copyright (C) 2025 Nicholas Acord <ncacord@protonmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact: ncacord@protonmail.com


"""
main.py — Entry point for RaidAssist.
Fetches and caches the Destiny 2 Bungie profile for the user.

Usage:
- Set BUNGIE_API_KEY, MEMBERSHIP_TYPE, and MEMBERSHIP_ID as environment variables
  or replace the placeholders below.
"""

import os
import logging
from api.bungie import fetch_profile

# Optional: log to file if desired
LOG_PATH = "RaidAssist/logs/main.log"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

if __name__ == "__main__":
    # Set these with environment variables or direct assignment
    membership_type = os.environ.get(
        "MEMBERSHIP_TYPE", 3
    )  # 1=Xbox, 2=PSN, 3=Steam, etc.
    membership_id = os.environ.get("MEMBERSHIP_ID", "YOUR_MEMBERSHIP_ID")

    print("Fetching Bungie profile...")
    try:
        data = fetch_profile(membership_type, membership_id)
        if data:
            print("Profile data fetched and cached successfully.")
        else:
            print("Failed to fetch profile data.")
    except Exception as e:
        logging.error(f"Profile fetch failed: {e}")
        print(f"Error fetching profile: {e}")
