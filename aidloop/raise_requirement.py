import json
import math

import streamlit as st
import streamlit.components.v1 as components

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


# ── Session-state keys ─────────────────────────────────────────────────
_LOC_STEP = "raise_loc_step"  # idle | waiting | verified | denied
_LOC_LAT = "raise_loc_lat"
_LOC_LNG = "raise_loc_lng"
_LOC_DIST = "raise_loc_dist"
_LOC_ERR = "raise_loc_err"

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

    st.info("📍 **Verifying your location…** Please allow location access when prompted by your browser.")

    LOCATION_HTML = """
    <div id="status" style="text-align:center;padding:20px;font-size:16px;color:#555;">
      Requesting your location…
    </div>
    <script>
    function sendResult() {
      navigator.geolocation.getCurrentPosition(
        function (pos) {
          window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: JSON.stringify({
              lat: pos.coords.latitude,
              lng: pos.coords.longitude,
              error: null
            })
          }, '*');
        },
        function (err) {
          window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: JSON.stringify({
              lat: null,
              lng: null,
              error: err.message
            })
          }, '*');
        },
        { enableHighAccuracy: true, timeout: 15_000, maximumAge: 0 }
      );
    }
    // Try sending the result repeatedly until Streamlit picks it up.
    sendResult();
    setInterval(sendResult, 2000);
    </script>
    """

    location_data = components.html(LOCATION_HTML, height=60, key="raise-location-finder")

    # components.html returns a DeltaGenerator on first call,
    # and the actual value (string or None) on subsequent reruns.
    if isinstance(location_data, str):
        data = json.loads(location_data)
        if data.get("error"):
            st.session_state[_LOC_STEP] = "denied"
            st.session_state[_LOC_ERR] = data["error"]
        else:
            user_lat = data["lat"]
            user_lng = data["lng"]
            dist = _haversine_km(JANTAR_MANTAR_LAT, JANTAR_MANTAR_LNG, user_lat, user_lng)
            st.session_state[_LOC_LAT] = user_lat
            st.session_state[_LOC_LNG] = user_lng
            st.session_state[_LOC_DIST] = round(dist, 2)
            if dist <= MAX_DISTANCE_KM:
                st.session_state[_LOC_STEP] = "verified"
            else:
                st.session_state[_LOC_STEP] = "denied"
                st.session_state[_LOC_ERR] = (
                    f"You are **{dist:.1f} km** from Jantar Mantar, "
                    f"which is outside the **{MAX_DISTANCE_KM} km** allowed range."
                )
        st.rerun()


# ── Location denied → show error ──────────────────────────────────────
if st.session_state[_LOC_STEP] == "denied":

    st.error("❌ **Location verification failed**")

    err_msg = st.session_state.get(_LOC_ERR, "")
    if "km" in err_msg:
        st.warning(
            f"You are **{st.session_state.get(_LOC_DIST, '?')} km** "
            f"from Jantar Mantar. You need to be within **{MAX_DISTANCE_KM} km** "
            "to raise a requirement."
        )
    else:
        st.warning(
            "We need proof that you are in the nearby protest area so that we can "
            "prevent misuse. Please enable location access in your browser settings "
            "and try again."
        )

    col1, col2 = st.columns(2)
    if col1.button("🔄 Try Again", use_container_width=True):
        st.session_state[_LOC_STEP] = "idle"
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
    st.rerun()