import streamlit as st
from db import get_fulfilled_requirements

st.title("✅ Fulfilled Requirements")
st.markdown("Browse requirements that have been fulfilled, with proof of delivery/payment.")

fulfilled_reqs = get_fulfilled_requirements()

if not fulfilled_reqs:
    st.info("📭 No requirements have been fulfilled yet. Be the first!")
    st.page_link("fulfill_requirement.py", label="🤝 Fulfill a Requirement")
else:
    for req in fulfilled_reqs:
        with st.container(border=True):
            col1, col2 = st.columns([3, 2])

            with col1:
                st.markdown(f"### {req['item_name']}")
                st.markdown(f"**Quantity:** {req['quantity']}")
                if req["raiser_name"]:
                    st.markdown(f"**Raised by:** {req['raiser_name']}")
                if req["fulfiller_name"]:
                    st.markdown(f"**Fulfilled by:** {req['fulfiller_name']}")
                st.markdown(f"**Posted:** {req['created_at']}")
                st.markdown(f"**Fulfilled on:** {req['fulfilled_at']}")

            with col2:
                proof_path = req["proof_path"]
                if proof_path and proof_path.startswith("http"):
                    # Supabase public URL
                    st.image(proof_path, caption="Proof of delivery/payment", use_container_width=True)
                else:
                    st.warning("📷 Proof image not available.")