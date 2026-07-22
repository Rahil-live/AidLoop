# Architecture — AidLoop

## Stack
- **Frontend + backend**: Streamlit (Python) — single framework, no separate API layer
- **Data store**: SQLite (`aidloop.db`) for v1 → move to Supabase (Postgres + Storage) once you need real persistence
- **Image storage**: local `/uploads` for v1 → Supabase Storage / Cloudinary for production
- **Hosting**: Streamlit Community Cloud (free) for v1

## Why not just `st.session_state`?
Session state lives per browser tab. Here, the person who raises a requirement and the person who later fulfills it are two different sessions entirely — so the data has to live in a shared store (SQLite / hosted DB), not session state.

## Pages & flow
Use `st.navigation` + `st.Page` — the current preferred multipage API (the simpler `pages/`-folder auto-detection also works if you don't need dynamic nav):

```python
# app.py (entrypoint / router)
import streamlit as st

pg = st.navigation([
    st.Page("home.py", title="Home", default=True),
    st.Page("raise_requirement.py", title="🙋 Raise a Requirement"),
    st.Page("fulfill_requirement.py", title="🤝 Fulfill a Requirement"),
    st.Page("fulfilled.py", title="✅ Fulfilled Requirements"),
])
pg.run()
```
`home.py` just needs two `st.page_link()` calls for the "two faces" landing screen.

## Data model (`requirements` table)
| column | type | notes |
|---|---|---|
| id | INTEGER PK | autoincrement |
| item_name | TEXT | required |
| quantity | TEXT | keep as text ("50", "20 kg") — skip unit-parsing for v1 |
| raiser_name | TEXT | optional |
| status | TEXT | `open` \| `fulfilled` |
| fulfiller_name | TEXT | optional |
| proof_path | TEXT | path/URL to uploaded screenshot |
| created_at | TIMESTAMP | default now |
| fulfilled_at | TIMESTAMP | null until fulfilled |

## Core flow logic
- **Raise**: form (item_name, quantity, raiser_name) → validate not-empty → `INSERT ... status='open'`
- **Fulfill**: `SELECT * WHERE status='open'` → user picks one → `st.file_uploader(type=["png","jpg","jpeg"])` → on submit, save file + `UPDATE status='fulfilled', proof_path=..., fulfilled_at=now()`
- **Fulfilled tab**: `SELECT * WHERE status='fulfilled'` → render each row + its proof image (`st.image`)

## Ad banner — reality check
Streamlit has no built-in ad slot, and *where you host* matters more than the code:
- **v1, works anywhere, $0**: a self-managed sponsor/affiliate banner —
  ```python
  st.markdown(
      '<a href="LINK" target="_blank"><img src="BANNER_URL" style="width:100%"></a>',
      unsafe_allow_html=True
  )
  ```
  Put this once in `home.py` — it'll show on every page, since `home.py`'s code runs as the shared "frame" around pages when using `st.navigation`. No approval, no domain needed.
- **Real ad networks need a domain you own** — AdSense rejects `*.streamlit.app` outright (it requires a real top-level domain), and most free PaaS tiers gate custom domains behind a paid plan too (true of Render and Fly.io, not just Community Cloud — check before assuming otherwise). Free TLDs (`.tk`/`.ml`) are blacklisted by most ad networks, so budget ~$1–8/yr for a real domain (Namecheap/Porkbun) rather than chasing a free one.
- **Two ways to get a real domain without paying for hosting**:
  - **Oracle Cloud "Always Free"** — a real VM (2 vCPU/12GB RAM as of the 2026 revision), no time limit. Run Streamlit plus your own reverse proxy (Caddy/Nginx) on it and point your domain straight at the VM — full control, no platform gate. Needs a card for identity verification (not charged unless you upgrade); occasionally out of capacity in a given region, so try another if that happens.
  - **Split the app from the ad page**: keep Streamlit on any free host's subdomain (no cost), and build a small static "about" page on your own domain via Netlify/Vercel (both give free custom domains) that embeds the app in an iframe. Ads sit on that wrapper page, not inside the app itself.
- **Which network**: AdSense wants traffic history and a $100 payout minimum — rough for day one. Media.net (contextual) or Ezoic's "Access Now" tier (from ~50 visits/day) approve new sites faster and feel more legitimate. Adsterra/PropellerAds/Monetag approve instantly too, but lean toward popunders and push-notification ads — weigh that against the trust you're building with a relief app.
- Keep whichever banner above/beside the flow, not blocking the Raise/Fulfill buttons — an intrusive ad undercuts the trust you're trying to build for a relief app.

## Persistence caveat
Community Cloud's filesystem isn't guaranteed to survive app restarts/redeploys — fine for a demo, not fine for something you want "live" long-term. Move `aidloop.db` and uploaded images to Supabase once the local version works.

## Suggested repo layout
```
aidloop/
├── app.py                   # router (st.navigation)
├── home.py
├── raise_requirement.py
├── fulfill_requirement.py
├── fulfilled.py
├── db.py                     # all read/write functions
├── uploads/                  # v1 only — gitignore
├── requirements.txt
└── README.md
```

## Input handling checklist
- Reject empty `item_name` / `quantity` before insert
- Restrict uploads to image types, cap size (~5MB)
- Sanitize filenames before saving (strip path separators)
