## ▶️ **PROJECT BRIEF — v2**

Design a **self-hosted Instagram intelligence dashboard** that:

* Scrapes **followers / followings / mutuals** for any handle (public **or** private with credentials).
* Stores every crawl in a local DB and lets me browse, filter, chart, and export.
* Ships a touch-friendly, dark-mode UI that works on phones, tablets, laptops.
* Runs headless on my Windows 11 box at boot (`http://localhost:8000`), reachable over **Tailscale**.
* One-click XLSX/CSV downloads plus auto-archived backups.

---

## 📐 **FUNCTIONAL SPECS**

### 1. Scraping core

Identical scraper stack as v1 (GraphQL + instagrapi fallback) with three extra data points per node:

| Field             | GraphQL key            | Private-API key   | Purpose           |
| ----------------- | ---------------------- | ----------------- | ----------------- |
| `profile_pic_url` | `node.profile_pic_url` | `profile_pic_url` | thumbnail grid    |
| `is_verified`     | `node.is_verified`     | `is_verified`     | UI badge          |
| `full_name`       | `node.full_name`       | `full_name`       | searchable column |

GraphQL keeps exposing those keys in `edge_followed_by/edge_follow` nodes as of April 2025. ([Stack Overflow][1])

### 2. Persistent storage & caching

* **SQLite** via SQLModel; tables: `accounts`, `scrapes`, `followers`.
* Each scrape inserts follower rows with a composite PK `(target_id, follower_id)` to de-dupe.
* Delta calc job marks *new* vs *lost* followers between scrapes.
* Redis (optional) layer caches last 24 h API payloads to soften rate limits.

### 3. API & background tasks

* **FastAPI** still, but wire **RQ** (Redis Queue) for long-running scrape jobs so UI stays snappy.
* `/api/scrape` enqueues, `/api/progress/{job_id}` streams SSE status.
* Daily scheduled job refreshes bookmarked accounts at 02:00 local.

### 4. UI / UX overhaul

| Zone                 | Elements                                                                                                                                   | Notes                                 |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------- |
| **Sidebar**          | logo, theme switch, nav items (“Dashboard”, “Accounts”, “Scrapes”, “Settings”)                                                             | collapsible on mobile                 |
| **Dashboard (home)** | KPI cards (total scraped accts, rows, last run), mini-chart “Top 5 Growth”, global search bar                                              | line charts via **Recharts**          |
| **Accounts page**    | searchable table (shadcn `DataTable`) listing each target; right-side “Actions” column (Run scrape / View data / Delete)                   | infinite scroll                       |
| **Followers view**   | tab set: **Followers**, **Following**, **Mutuals**; data grid shows avatar, @handle (click opens IG in new tab), full name, verified badge | filters (search, only new, only lost) |
| **Scrape modal**     | input detects “@username” vs full URL; checkboxes to get Followers / Following / Both; toggle “Use private creds if needed”                | shows live progress bar               |
| **Exports panel**    | dropdown to choose format (CSV/XLSX/JSON); “Download” button; “Open in Excel Online” deep link on desktop                                  | iOS Safari downloads via Blob         |
| **Settings**         | encrypted-creds setup, proxy list, rate-limit sliders, backup retention days                                                               | Credential status indicator           |

All components responsive ≥320 px, 44 px tap targets, motion reduced by `prefers-reduced-motion`.

### 5. Data visualisation bonus

* “Follow-back spider chart” (followers you don’t follow back vs vice-versa).
* Timeline chart: follower count per scrape (Sparkline).
* Mutual-network explorer (sigma.js) optional stretch goal.

### 6. Security & creds

* Same AES-256 encrypted `.env` flow as v1; master key lives in **Windows Credential Manager**.
* Optional **passphrase unlock modal** at app start on remote clients.
* CSRF & CORS locked to tailnet.

### 7. Deployment & startup

* Provide **Docker Compose** (backend, redis, frontend Nginx).
* Non-Docker path: `pip install -r requirements.txt && npm run build && nssm install ...`.
* README snippet to add `uvicorn` service to NSSM so Windows starts it.

---

## 🛠 **TECH STACK (locked)**

Python 3.11 · FastAPI · RQ + Redis · SQLModel · instagrapi · React 18 · Vite · TailwindCSS · shadcn/ui · Recharts · sigma.js · Docker · nssm

---

## 📝 **DELIVERABLES**

1. `backend/` – API + worker + models + tests
2. `frontend/` – React app (src/, vite.config.ts, postcss.config.js)
3. `scripts/` – `generate_env.py`, `backup_cleaner.py`
4. `docker-compose.yml`
5. `README.md` – install, creds, Tailscale, Windows-service steps
6. `.github/workflows/ci.yml` – lint, test, build
7. `docs/ER_diagram.png` – entity-relation diagram
