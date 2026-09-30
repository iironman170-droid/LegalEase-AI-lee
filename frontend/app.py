import html
import os
import tempfile
from pathlib import Path

import requests
import streamlit as st


from backend.document_utils.formatters import (
    format_docx,
    format_pdf,
    format_txt,
)


# =========================================================
# Streamlit configuration
# =========================================================

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


# =========================================================
# Backend configuration
# =========================================================

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
)


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]


LOGO_PATH = (
    PROJECT_ROOT
    / "assets"
    / "logo.png"
)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
<style>

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    margin-top: 10px;
}

.subtitle {
    text-align: center;
    color: #94a3b8;
    font-size: 17px;
    margin-bottom: 30px;
}

.preview-box {
    background-color: #0f172a;
    color: #e2e8f0;
    padding: 30px;
    border-radius: 15px;
    border: 1px solid #334155;
    max-height: 650px;
    overflow-y: auto;
    white-space: pre-wrap;
    line-height: 1.7;
    font-family: Georgia, serif;
}

.disclaimer {
    background-color: #0f172a;
    border-left: 4px solid #38bdf8;
    padding: 15px;
    margin-top: 20px;
    color: #94a3b8;
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# Logo
# =========================================================

if LOGO_PATH.exists():

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        st.image(
            str(LOGO_PATH),
            width=130,
        )


# =========================================================
# Header
# =========================================================

st.markdown(
    '<div class="main-title">LegalEase</div>',
    unsafe_allow_html=True,
)


st.markdown(
    """
<div class="subtitle">
AI-Powered Legal Document Generator
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# Session state
# =========================================================

if "document" not in st.session_state:

    st.session_state.document = ""


if "document_type" not in st.session_state:

    st.session_state.document_type = ""


if "terms" not in st.session_state:

    st.session_state.terms = ""


if "disclaimer" not in st.session_state:

    st.session_state.disclaimer = ""


# =========================================================
# Sidebar
# =========================================================

with st.sidebar:

    st.header(
        "Document Information"
    )


    document_type = st.text_input(
        "Document Type",
        placeholder=(
            "Example: NDA"
        ),
    )


    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Example: John Doe (Freelancer), "
            "ABC Corporation (Client)"
        ),
        height=120,
    )


    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Enter terms separated by semicolons (;)"
        ),
        height=200,
    )


    dates = st.text_input(
        "Effective Date",
        placeholder=(
            "Example: October 1, 2026"
        ),
    )


    jurisdiction = st.text_input(
        "Jurisdiction (Optional)",
        placeholder=(
            "Example: Tamil Nadu, India"
        ),
    )


    uploaded_logo = st.file_uploader(
        "Upload Custom Logo",
        type=[
            "png",
            "jpg",
            "jpeg",
        ],
    )


    generate_button = st.button(
        "Generate Document",
        type="primary",
        use_container_width=True,
    )


# =========================================================
# Generate document
# =========================================================

if generate_button:

    if not document_type.strip():

        st.error(
            "Please enter the document type."
        )

        st.stop()


    if not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

        st.stop()


    if not terms.strip():

        st.error(
            "Please enter the terms and conditions."
        )

        st.stop()


    if not dates.strip():

        st.error(
            "Please enter the effective date."
        )

        st.stop()


    request_data = {

        "document_type":
            document_type,

        "parties":
            parties,

        "terms":
            terms,

        "dates":
            dates,

        "jurisdiction":
            jurisdiction
            if jurisdiction.strip()
            else None,
    }


    try:

        with st.spinner(
            "Generating legal document..."
        ):

            response = requests.post(
                f"{BACKEND_URL}/generate",
                json=request_data,
                timeout=180,
            )


        if response.status_code == 200:

            result = response.json()


            st.session_state.document = (
                result["content"]
            )


            st.session_state.document_type = (
                result["document_type"]
            )


            st.session_state.terms = terms


            st.session_state.disclaimer = (
                result["disclaimer"]
            )


            st.success(
                "Document generated successfully!"
            )


        else:

            try:

                error_message = (
                    response.json()
                    .get(
                        "detail",
                        response.text,
                    )
                )

            except Exception:

                error_message = response.text


            st.error(
                f"Backend error: "
                f"{error_message}"
            )


    except requests.exceptions.ConnectionError:

        st.error(
            "Cannot connect to the FastAPI backend."
        )

        st.info(
            "Start the backend using:"
        )

        st.code(
            "uvicorn backend.main:app --reload"
        )


    except requests.exceptions.Timeout:

        st.error(
            "The request timed out. "
            "Please try again."
        )


    except Exception as error:

        st.error(
            f"Unexpected error: {error}"
        )


# =========================================================
# Document result
# =========================================================

if st.session_state.document:

    st.markdown(
        "## Generated Document"
    )


    preview_tab, edit_tab = st.tabs(
        [
            "Preview",
            "Edit Document",
        ]
    )


    # =====================================================
    # Preview
    # =====================================================

    with preview_tab:

        safe_document = html.escape(
            st.session_state.document
        )


        st.markdown(
            f"""
<div class="preview-box">
{safe_document}
</div>
""",
            unsafe_allow_html=True,
        )


    # =====================================================
    # Edit
    # =====================================================

    with edit_tab:

        edited_document = st.text_area(
            "Edit your document below:",
            value=(
                st.session_state.document
            ),
            height=650,
        )


        if st.button(
            "Save Edits",
            type="primary",
        ):

            st.session_state.document = (
                edited_document
            )


            st.success(
                "Your edits have been saved."
            )


    # =====================================================
    # Downloads
    # =====================================================

    st.markdown(
        "## Download Document"
    )


    col1, col2, col3 = st.columns(3)


    current_document = (
        st.session_state.document
    )


    current_type = (
        st.session_state.document_type
    )


    filename = "".join(
        character
        if character.isalnum()
        else "_"
        for character in current_type
    ).strip("_")


    if not filename:

        filename = "LegalEase_Document"


    # =====================================================
    # TXT
    # =====================================================

    with col1:

        txt_file = format_txt(
            current_document
        )


        st.download_button(
            "Download TXT",
            data=txt_file,
            file_name=f"{filename}.txt",
            mime="text/plain",
            use_container_width=True,
        )


    # =====================================================
    # DOCX
    # =====================================================

    with col2:

        logo_bytes = None


        if uploaded_logo:

            logo_bytes = (
                uploaded_logo.getvalue()
            )


        docx_file = format_docx(
            text=current_document,
            document_type=current_type,
            terms=st.session_state.terms,
            logo_bytes=logo_bytes,
        )


        st.download_button(
            "Download DOCX",
            data=docx_file,
            file_name=f"{filename}.docx",
            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.wordprocessingml.document"
            ),
            use_container_width=True,
        )


    # =====================================================
    # PDF
    # =====================================================

    with col3:

        temporary_logo = None


        try:

            logo_path = None


            if uploaded_logo:

                suffix = (
                    Path(
                        uploaded_logo.name
                    ).suffix
                    or ".png"
                )


                temporary = (
                    tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=suffix,
                    )
                )


                temporary.write(
                    uploaded_logo.getvalue()
                )


                temporary.close()


                temporary_logo = (
                    temporary.name
                )


                logo_path = (
                    temporary_logo
                )


            pdf_file = format_pdf(
                text=current_document,
                document_type=current_type,
                logo_path=logo_path,
            )


            st.download_button(
                "Download PDF",
                data=pdf_file,
                file_name=f"{filename}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )


        finally:

            if temporary_logo:

                try:

                    os.unlink(
                        temporary_logo
                    )

                except OSError:

                    pass


    # =====================================================
    # Disclaimer
    # =====================================================

    st.markdown(
        f"""
<div class="disclaimer">
{html.escape(st.session_state.disclaimer)}
</div>
""",
        unsafe_allow_html=True,
    )


else:

    st.info(
        "Enter the document details from the sidebar "
        "and click Generate Document."
    )