# AidLoop 🔄

A lightweight Streamlit web app for coordinating relief supplies. People on the ground can post what's needed, and anyone can browse open requirements, provide items off-app, and upload proof to close the loop.

**Data is persistently stored in Supabase (Postgres + Storage) — shared by all users, survives restarts.**

## Features

- **🙋 Raise a Requirement** — Post a need (item + quantity) with an optional name
- **🤝 Fulfill a Requirement** — Browse open requirements, pick one, deliver off-app, upload proof (screenshot)
- **✅ Fulfilled Requirements** — Browse completed requirements with proof images

## Stack

- **Frontend + Backend**: Streamlit (Python)
- **Database**: Supabase (Postgres)
- **Image Storage**: Supabase Storage (S3-compatible)
- **Hosting**: Streamlit Community Cloud

## Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure secrets
# Create .streamlit/secrets.toml with:
# supabase_url = "https://your-project.supabase.co"
# supabase_key = "your-anon-key"

# 3. Run the app
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

## Project Structure

```
aidloop/
├── .streamlit/
│   ├── config.toml          # Streamlit theme & settings
│   └── secrets.toml          # Supabase credentials (gitignored)
├── app.py                   # Router (st.navigation)
├── home.py                  # Landing page with two entry points
├── raise_requirement.py     # Raise a Requirement form
├── fulfill_requirement.py   # Fulfill a Requirement flow
├── fulfilled.py             # Fulfilled requirements view
├── db.py                    # Supabase read/write functions
├── requirements.txt
├── .gitignore
└── README.md
```

## Deployment on Streamlit Cloud

1. Push code to GitHub
2. Go to https://streamlit.io/cloud → New app → select repo
3. Set **Main file path** to `aidloop/app.py`
4. In Streamlit Cloud dashboard → **Settings** → **Secrets**, add:

```toml
supabase_url = "https://your-project.supabase.co"
supabase_key = "your-anon-key"
```

5. Deploy!

## Supabase Setup

The project expects a Supabase project with:

1. **Table `requirements`** — run this SQL in the SQL Editor:

```sql
CREATE TABLE requirements (
    id BIGSERIAL PRIMARY KEY,
    item_name TEXT NOT NULL,
    quantity TEXT NOT NULL,
    raiser_name TEXT DEFAULT ''::text,
    status TEXT NOT NULL DEFAULT 'open'::text,
    fulfiller_name TEXT DEFAULT ''::text,
    proof_path TEXT DEFAULT ''::text,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    fulfilled_at TIMESTAMPTZ
);

ALTER TABLE requirements ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read requirements"
    ON requirements FOR SELECT USING (true);

CREATE POLICY "Anyone can insert requirements"
    ON requirements FOR INSERT WITH CHECK (true);

CREATE POLICY "Anyone can update requirements"
    ON requirements FOR UPDATE USING (true);
```

2. **Storage bucket** `proof-images` — set to **Public bucket**