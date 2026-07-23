import streamlit as st
import streamlit.components.v1 as components

from database import init_db, get_request_counts
from ts_animation import (
    load_ts_mode,
    generate_xyz_frames,
    build_ts_viewer,
)

st.set_page_config(
    page_title="DFT Portal",
    page_icon="🧪",
    layout="wide",
)

init_db()

st.title("MCK Lab: DFT Portal")

st.caption("Submit, review, and track computational chemistry requests.")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button(
        "Submit a Calculation",
        use_container_width=True,
        type="primary",
    ):
        st.switch_page("pages/1_Submit_Request.py")

with col2:
    if st.button(
        "View Calculations",
        use_container_width=True,
    ):
        st.switch_page("pages/2_View_Requests.py")

with col3:
    if st.button(
        "Information",
        use_container_width=True,
    ):
        st.switch_page("pages/4_Information.py")

st.divider()

ts_files = [
    "structures/ts_01.log",
    "structures/ts_02.log",
    "structures/ts_03.log",
]

cols = st.columns(3)

for col, log_path in zip(cols, ts_files):

    with col:

        try:
            ts_data = load_ts_mode(log_path)

            frames = generate_xyz_frames(
                coords=ts_data["coords"],
                atomic_numbers=ts_data["atomic_numbers"],
                displacement=ts_data["displacement"],
                frequency=ts_data["frequency"],
                n_frames=30,
                amplitude=0.7,
            )

            viewer = build_ts_viewer(
                frames,
                width=380,
                height=350,
            )

            viewer_html = viewer._make_html()

            bordered_html = f"""
            <div style="
                border: 1px solid #222;
                border-radius: 6px;
                overflow: hidden;
                width: 100%;
                box-sizing: border-box;
                background-color: white;
            ">
                {viewer_html}
            </div>
            """

            components.html(
                bordered_html,
                height=370,
                scrolling=False,
            )

        except Exception as exc:
            st.warning(
                f"Could not load {log_path}: {exc}"
            )

st.markdown(
    """
    <div style="
        text-align: center;
        color: #6c757d;
        font-size: 1rem;
        margin-top: 18px;
        font-style: italic;
    ">
        “Everything that living things do can be understood in terms
        of the jiggling and wiggling of atoms.”
        <br>
        <b>— Richard Feynman</b>
    </div>
    """,
    unsafe_allow_html=True,
)
