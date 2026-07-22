import streamlit as st

# ── Ad banner (shown on every page because home.py acts as the shared frame) ──
# st.markdown(
#     '<a href="https://example.com" target="_blank">'
#     '<img src="https://placehold.co/728x90/EEE/333?text=Support+Relief+Efforts+%E2%80%94+Your+Ad+Here" '
#     'style="width:100%;border-radius:8px;"></a>',
#     unsafe_allow_html=True,
# )
st.divider()

# ── Hero ──
st.title("🔄 AidLoop For CJP")
st.title("Location is Jantar Mantar Protest Site, New Delhi")
st.markdown(
    """
    **Connecting those who need with those who can help.**

    A lightweight coordination layer for relief supplies — no login, no fuss.
    """
)
st.divider()

# ── Two entry points ──
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🙋 Need something?")
    st.markdown("Post what's required — food, water, medicine, daily essentials.")
    st.page_link(
        "raise_requirement.py",
        label="📝 Raise a Requirement",
        use_container_width=True,
    )

with col2:
    st.markdown("### 🤝 Want to help?")
    st.markdown("Browse open requirements, pick one, deliver off-app, and upload proof.")
    st.page_link(
        "fulfill_requirement.py",
        label="🎯 Fulfill a Requirement",
        use_container_width=True,
    )

st.divider()

# ── Quick glance at stats ──
from db import get_open_requirements, get_fulfilled_requirements

open_reqs = get_open_requirements()
fulfilled_reqs = get_fulfilled_requirements()

stats_col1, stats_col2 = st.columns(2)
stats_col1.metric("📋 Open Requirements", len(open_reqs))
stats_col2.metric("✅ Fulfilled", len(fulfilled_reqs))