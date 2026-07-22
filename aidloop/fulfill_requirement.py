import streamlit as st
from db import get_open_requirements, get_requirement_by_id, fulfill_requirement
from supabase import create_client
from io import BytesIO
from PIL import Image

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_IMAGE_DIMENSION = 1920  # px – resize longest side to this
COMPRESSION_QUALITY = 85    # JPEG quality 1–100
ALLOWED_TYPES = {"png", "jpg", "jpeg"}
STORAGE_BUCKET = "proof-image"


def get_supabase_storage():
    """Return a Supabase Storage client."""
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    client = create_client(url, key)
    return client.storage.from_(STORAGE_BUCKET)


def compress_image(file_bytes: bytes, max_dimension: int = MAX_IMAGE_DIMENSION, quality: int = COMPRESSION_QUALITY) -> bytes:
    """
    Open an image, resize the longest side to *max_dimension* (preserving aspect ratio),
    and re-encode as JPEG at the given *quality*. Returns the compressed bytes.
    """
    img = Image.open(BytesIO(file_bytes))
    # Convert RGBA / P-mode to RGB so we can save as JPEG
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    # Resize if the longest side exceeds max_dimension
    w, h = img.size
    if max(w, h) > max_dimension:
        ratio = max_dimension / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


st.title("🤝 Fulfill a Requirement")
st.markdown("Pick an open requirement, provide it off-app, and upload proof of delivery/payment.")

open_reqs = get_open_requirements()

if not open_reqs:
    st.info("🎉 No open requirements right now. Check back later, or raise one yourself!")
    st.page_link("raise_requirement.py", label="🙋 Raise a Requirement")
else:
    # Build a display label for each requirement – clean & readable
    options = {
        f"#{r['id']}  {r['item_name']}  (×{r['quantity']})"
        + (f"  —  {r['raiser_name']}" if r["raiser_name"] else "")
        : r["id"]
        for r in open_reqs
    }

    selected_label = st.selectbox(
        "Select a requirement to fulfill  👇",
        options=list(options.keys()),
        index=None,
        placeholder="Choose an open requirement…",
    )

    if selected_label is None:
        st.stop()

    selected_id = options[selected_label]

    req = get_requirement_by_id(selected_id)

    if req:
        with st.container(border=True):
            st.markdown(f"**Item:** {req['item_name']}")
            st.markdown(f"**Quantity:** {req['quantity']}")
            if req["raiser_name"]:
                st.markdown(f"**Raised by:** {req['raiser_name']}")
            st.markdown(f"**Posted on:** {req['created_at']}")

            # Show the raiser's proof photo for verification
            raiser_proof = req.get("raiser_proof_path", "")
            if raiser_proof:
                st.markdown("---")
                st.markdown("**📸 Raised with this proof photo:**")
                st.image(raiser_proof, use_container_width=True)

        st.divider()

        with st.form("fulfill_form", clear_on_submit=True):
            fulfiller_name = st.text_input(
                "Your name (optional)",
                placeholder="Anonymous if left blank",
            )
            proof_file = st.file_uploader(
                "Upload proof of delivery/payment *",
                type=list(ALLOWED_TYPES),
                help="Screenshot of UPI payment, delivery photo, etc. Max 5 MB.",
            )

            submitted = st.form_submit_button("✅ Mark as Fulfilled", use_container_width=True)

            if submitted:
                errors = []

                if proof_file is None:
                    errors.append("Proof image is required.")

                if proof_file is not None:
                    # Check file size
                    if proof_file.size > MAX_FILE_SIZE:
                        errors.append("File is too large. Maximum size is 5 MB.")
                    # Check file type by extension
                    ext = proof_file.name.rsplit(".", 1)[-1].lower() if "." in proof_file.name else ""
                    if ext not in ALLOWED_TYPES:
                        errors.append("Only PNG, JPG, and JPEG files are allowed.")

                if errors:
                    for err in errors:
                        st.error(err)
                else:
                    # Compress & upload to Supabase Storage
                    try:
                        storage = get_supabase_storage()
                        # Compress the image before uploading
                        compressed_bytes = compress_image(proof_file.getvalue())
                        # Save as .jpg regardless of original extension
                        dest_filename = f"{selected_id}_{proof_file.name.rsplit('.', 1)[0]}.jpg"
                        storage.upload(
                            dest_filename,
                            compressed_bytes,
                            {"content-type": "image/jpeg"},
                        )
                        # Get the public URL
                        public_url = storage.get_public_url(dest_filename)
                    except Exception as e:
                        st.error(f"Failed to upload proof image: {e}")
                        st.stop()

                    # Update DB with the public URL
                    success = fulfill_requirement(selected_id, fulfiller_name, public_url)
                    if success:
                        st.success(
                            f"✅ Requirement #{selected_id} has been marked as fulfilled! "
                            "Thank you for helping out."
                        )
                        st.balloons()
                    else:
                        st.error(
                            "Could not fulfill this requirement. "
                            "It may have already been fulfilled by someone else."
                        )