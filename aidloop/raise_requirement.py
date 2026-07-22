import streamlit as st
from db import insert_requirement

st.title("🙋 Raise a Requirement")
st.markdown("Post what's needed on the ground — food, water, medicine, daily essentials.")

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
            row_id = insert_requirement(item_name, quantity, raiser_name)
            st.success(f"✅ Requirement #{row_id} posted successfully!")
            st.balloons()