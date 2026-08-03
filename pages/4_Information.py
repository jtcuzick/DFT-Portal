import streamlit as st


st.set_page_config(
    page_title="DFT Learning Center",
    page_icon="📚",
    layout="wide",
)


# Hide Streamlit's automatic sidebar
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


if st.button("← Back to home"):
    st.switch_page("app.py")


st.title("DFT Learning Center")

st.caption(
    "Short articles explaining computational chemistry concepts, "
    "methods, and practical workflows."
)

st.divider()


articles = [
    {
        "title": "What Is Density Functional Theory?",
        "description": (
            "An introduction to electron density, the Kohn–Sham framework, "
            "and what a DFT calculation is actually approximating."
        ),
        "page": "pages/5_DFT_Basics.py",
        "tag": "Fundamentals",
    },
    {
        "title": "Choosing a Functional",
        "description": (
            "How B3LYP, M06-2X, ωB97X-D, PBE0, and related functionals "
            "differ—and why the best choice depends on the chemistry."
        ),
        "page": "pages/6_Functionals.py",
        "tag": "Methods",
    },
    {
        "title": "Understanding Basis Sets",
        "description": (
            "A practical guide to split valence, polarization, diffuse "
            "functions, and common Pople and def2 basis sets."
        ),
        "page": "pages/7_Basis_Sets.py",
        "tag": "Methods",
    },
    {
        "title": "Calculating Redox Potentials",
        "description": (
            "How solution-phase free energies are converted into reduction "
            "and oxidation potentials, including reference-electrode choices."
        ),
        "page": "pages/8_Redox_Potentials.py",
        "tag": "Applications",
    },
]


cols = st.columns(2)

for index, article in enumerate(articles):

    with cols[index % 2]:

        with st.container(border=True):

            st.caption(article["tag"])

            st.subheader(article["title"])

            st.write(article["description"])

            if st.button(
                "Read article",
                key=f"article_{index}",
                use_container_width=True,
            ):
                st.switch_page(article["page"])
