"""Home page for streamlit app.

Notes:
Chat input widget:
prompt = st.text_input("Ask a question about the paper")

Chat message container:
with st.chat_mesage("user"):
    st.markdown(prompt)

Status container:
with st.status("Generating response..."):
    response = get_response(prompt)

Write stream of text:
st.write_stream(my_generator)
"""

import streamlit as st
import google.generativeai as genai
import base64
from streamlit_pdf_viewer import pdf_viewer
import pyprojroot


GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

selected_model = "gemini-pro"
PDF_DIR = "data"

example_pdf = "vaswani_et_al_2017.pdf"


def show_pdf(file_path, method="Embed"):
    """Not working. Replaced with streamlit-pdf-viewer package."""
    if file_path is None:
        st.stop()
    with open(file_path, "rb") as loaded_file:
        base64_pdf = base64.b64encode(loaded_file.read()).decode("utf-8")
    if method == "Embed":
        pdf_display = (
            f'<embed src="data:application/pdf;base64,{base64_pdf}" '
            'width="700" height="1000" type="application/pdf"></embed>'
        )
    elif method == "Iframe":
        pdf_display = (
            f'<iframe src="data:application/pdf;base64,{base64_pdf}" '
            'width="700" height="1000" type="application/pdf"></iframe>'
        )
    elif method == "html":
        # Embedding PDF in HTML
        pdf_display = f"""<embed
        class="pdfobject"
        type="application/pdf"
        title="Embedded PDF"
        src="data:application/pdf;base64,{base64_pdf}"
        style="overflow: auto; width: 100%; height: 100%;">"""
    else:
        st.Error(f"Unknown method: {method}")
    st.markdown(pdf_display, unsafe_allow_html=True)


def get_response(messages, model="gemini-pro"):
    model = genai.GenerativeModel(model)
    res = model.generate_content(
        messages, stream=True, safety_settings={"HARASSMENT": "block_none"}
    )
    return res


def list_pdfs():
    # TODO move to src
    pdf_dict = {
        "Attention is All You Need": "vaswani_et_al_2017.pdf",
        "BERT": "devlin_et_al_2018.pdf",
        "Generative Adversarial Nets": "goodfellow_et_al_2014.pdf",
        "Playing Atari with Deep Reinforcement Learning": "mnih_et_al_2013.pdf",
        "ImageNet Classification with Deep Convolutional Neural Networks": "krizhevsky_et_al_2012.pdf",
    }
    return pdf_dict


def get_pdfs():
    # See arxiv_pdfs.ipynb. Need to move function into src
    # TODO use src function to verify pdfs are downloaded
    return


def main():

    # get_pdfs()
    # show_pdf(pyprojroot.here() / "data" / example_pdf, method="html")

    st.title("arXiv Chat")
    st.write("Chat with recent arXiv papers!")

    selected_pdf = example_pdf
    pdf_dict = list_pdfs()
    selected_pdf_key = st.selectbox("Select a PDF", list(pdf_dict.keys()))
    selected_pdf = pdf_dict[selected_pdf_key]

    with st.expander("Show PDF", expanded=True):
        pdf_viewer(
            pyprojroot.here() / "data" / selected_pdf,
            height=600,
            width=800,
            rendering="unwrap",  # "unwrap", "legacy_iframe", "legacy_embed"
        )

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
