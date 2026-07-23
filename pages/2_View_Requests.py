import pandas as pd
import streamlit as st

from database import get_all_requests, init_db

init_db()

st.title("DFT Requests")

requests = get_all_requests()

if not requests:
    st.info("No requests have been submitted yet.")
    st.stop()

status_options = sorted({r["status"] for r in requests})
selected_statuses = st.multiselect(
    "Filter by status",
    status_options,
    default=status_options,
)

search_term = st.text_input(
    "Search",
    placeholder="Person, project, molecule, calculation...",
).strip().lower()

filtered = []

for req in requests:
    if req["status"] not in selected_statuses:
        continue

    searchable = " ".join(
        str(req.get(field, "") or "")
        for field in [
            "submitted_by",
            "project",
            "molecule_name",
            "calculation_type",
            "scientific_question",
        ]
    ).lower()

    if search_term and search_term not in searchable:
        continue

    filtered.append(req)

table_rows = []

for req in filtered:
    table_rows.append(
        {
            "Request": f"DFT-{req['id']:04d}",
            "Person": req["submitted_by"],
            "Project": req["project"],
            "Molecule": req["molecule_name"],
            "Calculation": req["calculation_type"],
            "Status": req["status"],
            "Job ID": req["cluster_job_id"],
            "Submitted": req["submitted_at"],
            "Updated": req["updated_at"],
        }
    )

if table_rows:
    st.dataframe(
        pd.DataFrame(table_rows),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.warning("No requests match the current filters.")

st.divider()
st.subheader("Request details")

request_ids = {
    f"DFT-{req['id']:04d} — {req['molecule_name']}": req["id"]
    for req in filtered
}

if request_ids:
    selection = st.selectbox(
        "Open request",
        list(request_ids.keys()),
    )

    req = next(
        r for r in filtered
        if r["id"] == request_ids[selection]
    )

    st.markdown(f"### {selection}")
    st.write(f"**Submitted by:** {req['submitted_by']}")
    st.write(f"**Project:** {req['project'] or '—'}")
    st.write(f"**Calculation:** {req['calculation_type']}")
    st.write(f"**Status:** {req['status']}")
    st.write(f"**Charge / multiplicity:** {req['charge']} / {req['multiplicity']}")
    st.write(f"**Method preference:** {req['method_preference'] or '—'}")
    st.write(f"**Basis set:** {req['basis_set'] or '—'}")
    st.write(f"**Solvent:** {req['solvent'] or '—'}")

    st.markdown("**Scientific question**")
    st.write(req["scientific_question"])

    if req["admin_notes"]:
        st.markdown("**Admin notes**")
        st.write(req["admin_notes"])
