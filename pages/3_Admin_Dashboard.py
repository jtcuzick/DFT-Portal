import streamlit as st

from database import (
    VALID_STATUSES,
    get_all_requests,
    get_request_counts,
    init_db,
    update_request,
)

init_db()

st.title("Admin Dashboard")
st.caption("Review requests, track calculations, and record cluster job IDs.")

counts = get_request_counts()

cols = st.columns(4)
cols[0].metric("New", counts["Submitted"])
cols[1].metric("Reviewing", counts["Reviewing"])
cols[2].metric("Running", counts["Running"])
cols[3].metric("Complete", counts["Complete"])

st.divider()

requests = get_all_requests()

if not requests:
    st.info("No submitted calculations yet.")
    st.stop()

show_complete = st.checkbox("Show completed requests", value=False)

visible_requests = [
    r for r in requests
    if show_complete or r["status"] != "Complete"
]

labels = {
    (
        f"DFT-{r['id']:04d} | {r['submitted_by']} | "
        f"{r['molecule_name']} | {r['status']}"
    ): r
    for r in visible_requests
}

selected_label = st.selectbox(
    "Select request",
    list(labels.keys()),
)

req = labels[selected_label]

st.subheader(f"DFT-{req['id']:04d}: {req['molecule_name']}")

left, right = st.columns([2, 1])

with left:
    st.markdown("#### Scientific question")
    st.write(req["scientific_question"])

    st.markdown("#### Requested calculation")
    st.write(req["calculation_type"])

    st.markdown("#### Requester")
    st.write(req["submitted_by"])
    if req["email"]:
        st.write(req["email"])
    if req["project"]:
        st.write(f"Project: {req['project']}")

with right:
    st.markdown("#### Chemical details")
    st.write(f"Charge: **{req['charge']}**")
    st.write(f"Multiplicity: **{req['multiplicity']}**")
    st.write(f"Solvent: **{req['solvent'] or '—'}**")
    st.write(f"Method: **{req['method_preference'] or '—'}**")
    st.write(f"Basis: **{req['basis_set'] or '—'}**")

    if req["uploaded_file"]:
        st.success("Structure/input file attached")

st.divider()

with st.form("admin_update"):
    status_index = (
        VALID_STATUSES.index(req["status"])
        if req["status"] in VALID_STATUSES
        else 0
    )

    status = st.selectbox(
        "Status",
        VALID_STATUSES,
        index=status_index,
    )

    cluster_job_id = st.text_input(
        "Cluster job ID",
        value=req["cluster_job_id"] or "",
    )

    admin_notes = st.text_area(
        "Admin notes",
        value=req["admin_notes"] or "",
        height=160,
        placeholder=(
            "Example: Neutral optimized successfully. "
            "Radical anion optimization submitted."
        ),
    )

    save = st.form_submit_button(
        "Save changes",
        type="primary",
    )

if save:
    update_request(
        request_id=req["id"],
        status=status,
        admin_notes=admin_notes,
        cluster_job_id=cluster_job_id,
    )

    st.success("Request updated.")
    st.rerun()

st.divider()
st.subheader("Expanse submission")

st.info(
    "The cluster submission hook belongs here. "
    "Next we can connect this button to your existing "
    "generate_slurm_script(), upload_to_expanse(), and submit_slurm_file() functions."
)

st.button(
    "Approve & Submit to Expanse",
    disabled=True,
    help="Disabled until the existing Expanse engine is connected.",
)
