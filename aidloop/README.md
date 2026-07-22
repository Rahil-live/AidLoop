# AidLoop 🔄

A lightweight Streamlit web app for coordinating relief supplies. People on the ground can post what's needed, and anyone can browse open requirements, provide items off-app, and upload proof to close the loop.

## Features

- **🙋 Raise a Requirement** — Post a need (item + quantity) with an optional name
- **🤝 Fulfill a Requirement** — Browse open requirements, pick one, deliver off-app, upload proof (screenshot)
- **✅ Fulfilled Requirements** — Browse completed requirements with proof images

## Stack

- **Frontend + Backend**: Streamlit (Python)
- **Database**: SQLite (via `sqlite3` — stdlib)
- **Image Storage**: Local `uploads/` directory

## Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

## Project Structure

```
aidloop/
├── app.py                   # Router (st.navigation)
├── home.py                  # Landing page with two entry points
├── raise_requirement.py     # Raise a Requirement form
├── fulfill_requirement.py   # Fulfill a Requirement flow
├── fulfilled.py             # Fulfilled requirements view
├── db.py                    # Database read/write functions
├── uploads/                 # Uploaded proof images (gitignored)
├── requirements.txt
├── .gitignore
└── README.md
```

## Roadmap

- [ ] Move SQLite → Supabase (Postgres + Storage) for persistent hosting
- [ ] Add real ad network once a custom domain is available
- [ ] Moderator view for flagging spam
- [ ] Raiser confirmation loop (raiser marks requirement as truly fulfilled)