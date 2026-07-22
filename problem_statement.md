# Problem Statement — AidLoop
*(working name — rename freely)*

## Background
A student-led protest is currently ongoing in India. Participants are staying on-site for extended stretches and need a steady supply of food, water, and other daily essentials. Members of the public want to help, but have no easy way to know what's actually needed right now, or whether their help actually reached someone.

## The problem
There's no lightweight, public coordination layer between people who need something and people who can provide it — and no simple way to close the loop once help is given. Result: duplicate donations (everyone brings biryani, nobody brings water), unmet needs, and no trust signal for the donor.

## Goal
A Streamlit web app with two flows from one landing page:
1. **Raise a Requirement** — someone on the ground posts a need (item + quantity)
2. **Fulfill a Requirement** — someone else picks an open requirement, provides it off-app (pays via UPI / hand-delivers), and uploads proof (payment or delivery screenshot) to close it

## Users
- **Requirement Raiser** — posts a need
- **Fulfiller** — browses open requirements, fulfills one, uploads proof
- *(Future)* **Moderator** — reviews flagged/spam entries

## MVP scope
- No login — open access; name fields optional
- Landing page → two entry points (Raise / Fulfill)
- Requirement = item name + quantity, nothing more
- Fulfillment = pick one open requirement + upload exactly one proof image
- Three views: Raise form · Open requirements · Fulfilled requirements (with proof)
- One ad banner slot, present on every page

## Explicitly out of scope (v1)
- In-app payments — the app never touches money; all payment/delivery happens off-platform, the app only records proof of it
- Accounts, ratings, in-app chat between raiser and fulfiller
- Verifying that a proof screenshot is genuine
- Notifications (push / SMS / email)

## Risks to design around
- **Spam/fake requirements** — open posting means anyone can add junk; plan a report/hide flag for later
- **Sensitive data in screenshots** — payment screenshots can expose UPI IDs / account numbers; remind users in-app to crop or blur before upload
- **No verification loop** — "fulfilled" only means *someone* uploaded a screenshot, not that the raiser confirmed receipt; fine for v1, flag for v2 (raiser confirms)

## Monetization
- Non-intrusive ad banner — the app takes no cut of any donation, so ads are the only revenue path
- v1: a self-managed sponsor/affiliate banner
- Later: a real ad network, once you have your own domain (see `architecture.md` — Streamlit Community Cloud's shared subdomain rules this out for now)
