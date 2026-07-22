import math
import urllib.request
import urllib.error
import json

import streamlit as st

from db import insert_requirement

# ── Jantar Mantar (New Delhi) ──────────────────────────────────────────
JANTAR_MANTAR_LAT = 28.6272
JANTAR_MANTAR_LNG = 77.2165
MAX_DISTANCE_KM = 5.0


# ── Helpers ────────────────────────────────────────────────────────────
def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance in km between two GPS coordinates."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _get_ip_location() -> dict | None:
    """Look up the user's approximate location via ip-api.com (free, no key)."""
    try:
        req = urllib.request.Request(
            "http://ip-api.com/json/?fields=status,lat,lon,city,regionName,country",
            headers={"User-Agent": "AidLoop/1.0"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "success":
                return {
                    "lat": data["lat"],
                    "lng": data["lon"],
                    "city": data.get("city", ""),
                    "region": data.get("regionName", ""),
                    "country": data.get("country", ""),
                }
    except (urllib.error.URLError, json.JSONDecodeError, KeyError):
        pass
    return None


# ── Session-state keys ─────────────────────────────────────────────────
_LOC_STEP = "raise_loc_step"  # idle | waiting | verified | denied
_LOC_LAT = "raise_loc_lat"
_LOC_LNG = "raise_loc_lng"
_LOC_DIST = "raise_loc_dist"
_LOC_ERR = "raise_loc_err"
_LOC_DATA = "raise_geo_data"

if _LOC_STEP not in st.session_state:
    st.session_state[_LOC_STEP] = "idle"


# ── Page header ────────────────────────────────────────────────────────
st.title("🙋 Raise a Requirement")
st.markdown("Post what's needed on the ground — food, water, medicine, daily essentials.")


# ── The requirement form ───────────────────────────────────────────────
with st.form("raise_form", clear_on_submit=True):
    item_name = st.text_input(
        "Item name *",
        placeholder="e.g. Bottled water, packaged rice, face masks",
    )
    quantity = st.text_input(
        "Quantity *",
        placeholder="e.g. 50, 20 kg, 10 boxes",
    )
    raiser_name = st.text_input(
        "Your name (optional)",
        placeholder="Anonymous if left blank",
    )

    submitted = st.form_submit_button("📤 Submit Requirement", use_container_width=True)

    if submitted:
        errors = []
        if not item_name or not item_name.strip():
            errors.append("Item name is required.")
        if not quantity or not quantity.strip():
            errors.append("Quantity is required.")

        if errors:
            for err in errors:
                st.error(err)
        else:
            # ── Start location verification ────────────────────────────
            st.session_state[_LOC_STEP] = "waiting"
            st.session_state["raise_form_item"] = item_name
            st.session_state["raise_form_qty"] = quantity
            st.session_state["raise_form_name"] = raiser_name
            st.rerun()


# ── Location verification (runs after form submit) ─────────────────────
if st.session_state[_LOC_STEP] == "waiting":
    st.info("📍 **Verifying your approximate location via IP lookup…**")

    if _LOC_DATA in st.session_state:
        st.session_state[_LOC_STEP] = "verified" if st.session_state.get(_LOC_DIST, 0) <= MAX_DISTANCE_KM else "denied"
        st.rerun()

    with st.spinner("Looking up your location…"):
        geo = _get_ip_location()

    if geo is None:
        st.session_state[_LOC_STEP] = "denied"
        st.session_state[_LOC_ERR] = "Could not determine your location via IP lookup."
        st.rerun()

    dist = _haversine_km(JANTAR_MANTAR_LAT, JANTAR_MANTAR_LNG, geo["lat"], geo["lng"])
    st.session_state[_LOC_DATA] = geo
    st.session_state[_LOC_LAT] = geo["lat"]
    st.session_state[_LOC_LNG] = geo["lng"]
    st.session_state[_LOC_DIST] = round(dist, 2)

    if dist <= MAX_DISTANCE_KM:
        st.session_state[_LOC_STEP] = "verified"
    else:
        st.session_state[_LOC_STEP] = "denied"
        st.session_state[_LOC_ERR] = (
            f"You appear to be in **{geo['city']}, {geo['region']}** — "
            f"**{dist:.1f} km** from Jantar Mantar, "
            f"which is outside the **{MAX_DISTANCE_KM} km** allowed range."
        )
    st.rerun()


# ── Location denied → show error ──────────────────────────────────────
if st.session_state[_LOC_STEP] == "denied":

    st.error("❌ **Location verification failed**")

    err_msg = st.session_state.get(_LOC_ERR, "")
    if "km" in err_msg:
        st.warning(err_msg)
        st.markdown(
            "You need to be within **5 km of Jantar Mantar** to raise a requirement.",
        )
    else:
        st.warning(
            "We couldn't verify your location. This is needed to prevent misuse. "
            "Please check your internet connection and try again."
        )

    col1, col2 = st.columns(2)
    if col1.button("🔄 Try Again", use_container_width=True):
        st.session_state[_LOC_STEP] = "idle"
        st.session_state.pop(_LOC_DATA, None)
        st.rerun()
    if col2.button("🏠 Go Home"):
        st.switch_page("home.py")


# ── Location verified → insert requirement ────────────────────────────
if st.session_state[_LOC_STEP] == "verified":

    st.success(
        f"✅ **Location verified!** You are "
        f"**{st.session_state.get(_LOC_DIST, '?')} km** "
        f"from Jantar Mantar — within the allowed range."
    )

    item_name = st.session_state.get("raise_form_item", "")
    quantity = st.session_state.get("raise_form_qty", "")
    raiser_name = st.session_state.get("raise_form_name", "")

    row_id = insert_requirement(item_name, quantity, raiser_name)
    st.success(f"✅ Requirement #{row_id} posted successfully!")
    st.balloons()

    # Reset for next time
    st.session_state[_LOC_STEP] = "idle"
    st.session_state.pop(_LOC_DATA, None)
    st.rerun()