# pylint: disable=invalid-name
"""Home page for streamlit app"""

import streamlit as st
import google.generativeai as genai
import base64
import pyprojroot
import sys

from streamlit_pdf_viewer import pdf_viewer

sys.path.insert(0, str(pyprojroot.here()))  # Add parent directory to path
from src import utils  # pylint: disable=wrong-import-position

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

selected_model = "gemini-pro"
PDF_DIR = "data"
example_pdf = "krizhevsky_et_al_2012.pdf"

USE_ST_PDF_VIEWER = True


def get_response(messages, model=selected_model):
    model = genai.GenerativeModel(model)
    res = model.generate_content(
        messages, stream=True, safety_settings={"HARASSMENT": "block_none"}
    )
    return res


def get_pdf_dict():
    # Create a dictionary from "title" and "filename" in utils.local_papers
    pdf_dict = {}
    for _, value in utils.local_papers.items():
        pdf_dict[value["title"]] = value["filename"]
    return pdf_dict


def app_setup(silent=False):
    """Set up the app"""
    # Download PDFs if needed
    if (
        "pdfs_downloaded" not in st.session_state
        or not st.session_state["pdfs_downloaded"]
    ):
        utils.get_local_papers(silent=silent)
        st.session_state["pdfs_downloaded"] = True
    return


def display_pdf(file):
    pdf_viewer_width = 700
    pdf_viewer_height = 800
    method = "html"
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    if method == "iframe":
        # Note: iframe doesn't adjust width to the container
        pdf_display = f"""<iframe
                        src="data:application/pdf;base64,{base64_pdf}"
                        width="{pdf_viewer_width}"
                        height="{pdf_viewer_height}"
                        type="application/pdf">
                        </iframe>"""
    elif method == "html":
        pdf_display = f"""<embed
                        class="pdfobject"
                        type="application/pdf"
                        title="Embedded PDF"
                        src="data:application/pdf;base64,{base64_pdf}"
                        width="100%"
                        height="{pdf_viewer_height}"
                        >"""
        #               style="overflow: auto; width: 100%; height: 100%;"
    else:
        st.Error(f"Unknown method: {method}")
    st.markdown(pdf_display, unsafe_allow_html=True)
    return


def main():

    st.title("arXiv Chat")
    st.write("Chat with arXiv papers!")

    with st.spinner("Downloading papers..."):
        app_setup()

    selected_pdf = example_pdf
    pdf_dict = get_pdf_dict()
    selected_pdf_key = st.selectbox("Select a PDF", list(pdf_dict.keys()), index=4)
    selected_pdf = pdf_dict[selected_pdf_key]

    with st.expander("The paper", expanded=True):
        if USE_ST_PDF_VIEWER:
            pdf_viewer(
                pyprojroot.here() / "data" / selected_pdf,
                height=600,
                width=700,
                rendering="unwrap",  # "unwrap", "legacy_iframe", "legacy_embed"
            )
        else:
            display_pdf(pyprojroot.here() / "data" / selected_pdf)

    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    messages = st.session_state["messages"]

    chat_message = st.chat_input("Ask a question about the paper")

    with st.container(height=600):
        if messages:
            for item in messages:
                role, parts = item.values()
                if role == "user":
                    st.chat_message("user").markdown(parts[0])
                elif role == "model":
                    st.chat_message("assistant").markdown(parts[0])

        # chat_message = st.chat_input("Ask a question about the paper")

        if chat_message:
            st.chat_message("user").markdown(chat_message)
            res_area = st.chat_message("assistant").empty()

            messages.append(
                {"role": "user", "parts": [chat_message]},
            )
            res = get_response(messages)
            res_text = ""
            for chunk in res:
                res_text += chunk.text
                res_area.markdown(res_text)

            messages.append({"role": "model", "parts": [res_text]})

    return


if __name__ == "__main__":
    main()
