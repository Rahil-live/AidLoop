import streamlit as st
from db import insert_requirement
from supabase import create_client

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_TYPES = {"png", "jpg", "jpeg"}
STORAGE_BUCKET = "proof-image"


def get_supabase_storage():
    """Return a Supabase Storage client."""
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    client = create_client(url, key)
    return client.storage.from_(STORAGE_BUCKET)


st.title("🙋 Raise a Requirement")
st.markdown("Post what's needed on the ground — food, water, medicine, daily essentials.")

# ── Session-state keys for the upload/verify flow ──────────────────────
_STEP = "raise_step"          # form | uploading | done
_PENDING_ITEM = "raise_item"
_PENDING_QTY = "raise_qty"
_PENDING_NAME = "raise_name"
_PENDING_PHOTO = "raise_photo"

if _STEP not in st.session_state:
    st.session_state[_STEP] = "form"


# ── Step 1: Requirement form ──────────────────────────────────────────
if st.session_state[_STEP] == "form":

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
        proof_file = st.file_uploader(
            "Upload a photo of location for proof*",
            type=list(ALLOWED_TYPES),
            help="Take a picture of the situation on the ground. Max 5 MB.",
        )

        submitted = st.form_submit_button("📤 Submit Requirement", use_container_width=True)

        if submitted:
            errors = []
            if not item_name or not item_name.strip():
                errors.append("Item name is required.")
            if not quantity or not quantity.strip():
                errors.append("Quantity is required.")
            if proof_file is None:
                errors.append("Proof photo is required — show us the need on the ground.")
            elif proof_file.size > MAX_FILE_SIZE:
                errors.append("File is too large. Maximum size is 5 MB.")
            else:
                ext = proof_file.name.rsplit(".", 1)[-1].lower() if "." in proof_file.name else ""
                if ext not in ALLOWED_TYPES:
                    errors.append("Only PNG, JPG, and JPEG files are allowed.")

            if errors:
                for err in errors:
                    st.error(err)
            else:
                # Store form data in session state and move to upload step
                st.session_state[_PENDING_ITEM] = item_name
                st.session_state[_PENDING_QTY] = quantity
                st.session_state[_PENDING_NAME] = raiser_name
                st.session_state[_PENDING_PHOTO] = proof_file
                st.session_state[_STEP] = "uploading"
                st.rerun()


# ── Step 2: Upload proof photo to Supabase Storage, then insert ───────
if st.session_state[_STEP] == "uploading":
    with st.spinner("Uploading proof photo…"):
        try:
            storage = get_supabase_storage()
            proof_file = st.session_state[_PENDING_PHOTO]
            import time
            timestamp = int(time.time() * 1000)
            dest_filename = f"raiser_{timestamp}_{proof_file.name}"
            storage.upload(
                dest_filename,
                proof_file.getvalue(),
                {"content-type": proof_file.type or "image/png"},
            )
            public_url = storage.get_public_url(dest_filename)
        except Exception as e:
            st.error(f"Failed to upload proof photo: {e}")
            st.session_state[_STEP] = "form"
            st.stop()

    # Insert requirement with the proof URL
    item_name = st.session_state[_PENDING_ITEM]
    quantity = st.session_state[_PENDING_QTY]
    raiser_name = st.session_state[_PENDING_NAME]

    row_id = insert_requirement(
        item_name, quantity, raiser_name, raiser_proof_path=public_url
    )

    st.success(f"✅ Requirement #{row_id} posted successfully!")
    st.balloons()

    # Cleanup and reset
    for key in [_PENDING_ITEM, _PENDING_QTY, _PENDING_NAME, _PENDING_PHOTO]:
        st.session_state.pop(key, None)
    st.session_state[_STEP] = "done"
    st.rerun()


# ── Step 3: Done — offer navigation ───────────────────────────────────
if st.session_state[_STEP] == "done":
    st.info("Your requirement has been posted. What would you like to do next?")
    col1, col2 = st.columns(2)
    if col1.button("🏠 Go Home", use_container_width=True):
        st.session_state[_STEP] = "form"
        st.switch_page("home.py")
    if col2.button("🙋 Raise Another", use_container_width=True):
        st.session_state[_STEP] = "form"
        st.rerun()