from pathlib import Path

import streamlit as st

from database import create_request, init_db
from email_utils import send_request_notification

# Hide Streamlit's built-in sidebar

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }

        [data-testid="stSidebarCollapsedControl"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

init_db()

if st.button("← Back"):
    st.switch_page("app.py")

st.title("Submit a DFT Request")

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

st.caption(
    "Tell us the chemistry first. "
    "The computational details can be decided during review."
)


CALCULATION_TYPES = [
    "Radical Polarity",
    "Radical Stability",
    "Reduction Potential",
    "Oxidation Potential",
    "Bond Dissociation Energy",
    "Spin Density / Radical Analysis",
    "Nucleophilicity/Electrophilicity",
    "Transition-state search",
    "Electrostatic Map",
    "MO Visualization",
    "Other",
]


METHOD_OPTIONS = [
    "IDK, you decide!",
    "I know what method I want",
]


SOLVENT_OPTIONS = [
    "Gas phase",
    "Acetonitrile",
    "DMSO",
    "NMP",
    "DMF",
    "THF",
    "Dichloromethane",
    "Methanol",
    "Water",
    "Other / undecided",
]


# ==========================================================
# REQUESTER INFORMATION
# ==========================================================

st.subheader("Requester")

col1, col2 = st.columns(2)

with col1:
    submitted_by = st.text_input(
        "Name *"
    )

    project = st.text_input(
        "Project / collaboration"
    )

with col2:
    email = st.text_input(
        "Email *"
    )

    molecule_name = st.text_input(
        "Molecule / system name *"
    )


# ==========================================================
# SCIENTIFIC REQUEST
# ==========================================================

st.subheader("Scientific request")


calculation_type = st.selectbox(
    "What calculation do you think you need? *",
    CALCULATION_TYPES,
)


scientific_question = st.text_area(
    "What scientific question are you trying to answer? *",
    height=140,
    placeholder=(
        "Example: We want to know whether C–Br cleavage becomes "
        "thermodynamically favorable after one-electron reduction."
    ),
)


uploaded = st.file_uploader(
    "Upload a structure or Gaussian input",
    type=[
        "com",
        "gjf",
        "xyz",
        "mol",
        "sdf",
        "cdxml",
        "mol2",
    ],
)


# ==========================================================
# CHEMICAL DETAILS
# ==========================================================

st.subheader("Chemical details")

st.caption(
    "The following settings are optional. "
    "Only specify them if you have a particular computational method, "
    "basis set, charge/multiplicity, or solvent in mind. "
    "Otherwise, these parameters will be selected based on the "
    "computational requirements and chemical context of your request."
)


col3, col4 = st.columns(2)

with col3:
    charge = st.number_input(
        "Charge",
        step=1,
        value=0,
    )

with col4:
    multiplicity = st.number_input(
        "Multiplicity",
        min_value=1,
        step=1,
        value=1,
    )


# ==========================================================
# METHOD SELECTION
# ==========================================================

method_choice = st.radio(
    "Computational method",
    METHOD_OPTIONS,
)


basis_set = ""


if method_choice == "I know what method I want":

    col_method, col_basis = st.columns(2)

    with col_method:

        functional_choice = st.selectbox(
            "Functional / method",
            [
                "B3LYP",
                "B3LYP-D3",
                "M06",
                "M06-2X",
                "ωB97X-D",
                "ωB97X-D3",
                "PBE0",
                "CAM-B3LYP",
                "Other",
            ],
        )

        if functional_choice == "Other":

            method_detail = st.text_input(
                "Specify functional / method",
                placeholder="Enter functional or method",
            )

        else:

            method_detail = functional_choice


    with col_basis:

        basis_choice = st.selectbox(
            "Basis set",
            [
                "6-31G(d)",
                "6-31+G(d,p)",
                "6-311G(d,p)",
                "6-311+G(d,p)",
                "def2-SVP",
                "def2-TZVP",
                "def2-TZVPP",
                "Other",
            ],
        )

        if basis_choice == "Other":

            basis_set = st.text_input(
                "Specify basis set",
                placeholder="Enter basis set",
            )

        else:

            basis_set = basis_choice


    method_preference = method_detail

else:

    method_preference = method_choice
    basis_set = ""


# ==========================================================
# SOLVENT
# ==========================================================

solvent = st.selectbox(
    "Solvent / environment",
    SOLVENT_OPTIONS,
)


# ==========================================================
# SUBMIT BUTTON
# ==========================================================

submitted = st.button(
    "Submit request",
    type="primary",
    use_container_width=True,
)


# ==========================================================
# PROCESS SUBMISSION
# ==========================================================

if submitted:

    errors = []


    if not submitted_by.strip():
        errors.append(
            "Name is required."
        )


    if not email.strip():
        errors.append(
            "Email is required so we can send your ticket number."
        )


    if not molecule_name.strip():
        errors.append(
            "Molecule / system name is required."
        )


    if not scientific_question.strip():
        errors.append(
            "Scientific question is required."
        )


    if (
        method_choice == "I know what method I want"
        and not method_preference.strip()
    ):
        errors.append(
            "Please specify a functional / method."
        )


    if (
        method_choice == "I know what method I want"
        and not basis_set.strip()
    ):
        errors.append(
            "Please specify a basis set."
        )


    if errors:

        for error in errors:
            st.error(error)

    else:

        stored_path = None


        # ==================================================
        # SAVE UPLOADED FILE
        # ==================================================

        if uploaded is not None:

            safe_name = Path(
                uploaded.name
            ).name

            stored_path = (
                UPLOAD_DIR
                / safe_name
            )

            counter = 1

            while stored_path.exists():

                stored_path = (
                    UPLOAD_DIR
                    / (
                        f"{stored_path.stem}_"
                        f"{counter}"
                        f"{stored_path.suffix}"
                    )
                )

                counter += 1


            stored_path.write_bytes(
                uploaded.getbuffer()
            )


        # ==================================================
        # CREATE DATABASE REQUEST
        # ==================================================

        request_id = create_request(
            submitted_by=submitted_by.strip(),
            email=email.strip(),
            project=project.strip(),
            molecule_name=molecule_name.strip(),
            calculation_type=calculation_type,
            scientific_question=scientific_question.strip(),
            charge=int(charge),
            multiplicity=int(multiplicity),
            method_preference=method_preference,
            basis_set=basis_set,
            solvent=solvent,
            uploaded_file=(
                str(stored_path)
                if stored_path
                else None
            ),
        )


        ticket_number = (
            f"DFT-{request_id:04d}"
        )


        # ==================================================
        # EMAIL NOTIFICATIONS
        # ==================================================

        try:

            send_request_notification(
                request_id=request_id,
                requester_name=submitted_by.strip(),
                requester_email=email.strip(),
                molecule_name=molecule_name.strip(),
                calculation_type=calculation_type,
                scientific_question=scientific_question.strip(),
                admin_email="jcuzick@sas.upenn.edu",
            )

        except Exception as exc:

            st.warning(
                "The calculation request was saved, "
                "but the notification email could not be sent."
            )

            st.caption(
                f"Email error: {exc}"
            )


        # ==================================================
        # CONFIRMATION
        # ==================================================

        st.success(
            "Calculation received."
        )
