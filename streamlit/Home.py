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

DEFAULT_MODEL = "gemini-pro"
DEFAULT_SAFETY_SETTINGS = {"HARASSMENT": "block_none"}


def get_summary(pdf_text, model=DEFAULT_MODEL, safety_settings=None):
    # TODO switch to streaming output?
    # TODO Improve prompt
    # Note: Should always be preceded by "Instruction:"
    if safety_settings is None:
        safety_settings = DEFAULT_SAFETY_SETTINGS
    prompt = f"""
        Instruction: You are an AI researcher who has been asked to summarize the
        results of a scientific paper.
        Explain and summarize the scientifc results in the following text
        which has been extracted from a publication.

        Your response should have the form:

        "Summary"

        a paragraph of several sentences summarizing the results

        "Main result"

        a bullet point list of key results and concepts in the text

        ---
        {pdf_text}
        ---
        """
    prompt = f"""
        Instruction: Give a 1 sentence summary of the following text that has been
        extracted from a scientific paper.

        ---
        {pdf_text}
        ---
        """
    model = genai.GenerativeModel(model)
    response = model.generate_content(prompt, safety_settings=safety_settings)
    return response.text


def streaming_to_text(response):
    reponse_text = ""
    for chunk in response:
        reponse_text += chunk.text
    return reponse_text


def get_response(messages, model=DEFAULT_MODEL, safety_settings=None):
    if safety_settings is None:
        safety_settings = DEFAULT_SAFETY_SETTINGS
    model = genai.GenerativeModel(model)
    response = model.generate_content(messages, safety_settings=safety_settings)
    return response.text


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
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "pdf_text" not in st.session_state:
        st.session_state.pdf_text = {}
    if "pdf_summary" not in st.session_state:
        st.session_state.pdf_summary = {}
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


def write_messages_to_chat(messages):
    for item in messages:
        role, parts = item.values()
        # If the first message is an instruction, skip it
        if parts[0].startswith("Instructions:"):
            continue
        # Write message history to the chat area
        if role == "user":
            st.chat_message("user").markdown(parts[0])
        elif role == "model":
            st.chat_message("assistant").markdown(parts[0])
    return


def get_pre_message_prompt(pdf_text, pdf_summary):
    pre_message_text = f"""Instructions:
    You are helping an AI researcher who is learning about a paper.
    Below is the text of a paper and a summary of the paper.

    Here is the text of the paper:
    ---
    {pdf_text}
    ---

    Here is the summary of the paper:
    ---
    {pdf_summary}
    ---

    There may be a history of discussing others papers,
    but your job is to answer questions about this paper.
    Confirmed?
    """
    pre_message_prompt = []
    pre_message_prompt.append({"role": "user", "parts": [pre_message_text]})
    pre_message_prompt.append({"role": "Model", "parts": ["Confirmed!"]})
    return pre_message_prompt


def make_pirate(messages, is_pirate=False):
    pirate_command = "Arrr! Give new answers like a pirate, even if previous answers weren't pirate-like."
    not_pirate_command = "Do not give new answers like a pirate, even if previous answers were pirate-like."
    currently_pirate = messages[0]["parts"][0].endswith(pirate_command)
    # TODO: not implemented yet
    if is_pirate and not currently_pirate:
        # Need to add the command
        messages[0]["parts"][0] += pirate_command
    elif not is_pirate and currently_pirate:
        # Need to remove the command
        messages[0]["parts"][0] = messages[0]["parts"][0].replace(pirate_command, "")
    return messages


def main():

    st.title("arXiv Chat")
    st.write("Chat with arXiv papers!")

    with st.spinner("Downloading papers..."):
        app_setup()

    pdf_dict = get_pdf_dict()
    selected_pdf_key = st.selectbox("Select a PDF", list(pdf_dict.keys()), index=4)
    selected_pdf = pdf_dict[selected_pdf_key]
    pdf_path = pyprojroot.here() / "data" / selected_pdf

    use_better_pdf_viewer = st.toggle(
        "Use improved pdf viewer (may be incompatible with some browsers)", False
    )

    with st.expander("The paper", expanded=True):
        if use_better_pdf_viewer:
            display_pdf(pdf_path)
        else:
            pdf_viewer(
                pdf_path,
                height=600,
                width=700,
                rendering="unwrap",  # "unwrap", "legacy_iframe", "legacy_embed"
            )

    # Generate summary for selected pdf, selected_pdf is not a key in st.session_state.pdf_summary
    if selected_pdf not in st.session_state.pdf_summary:
        with st.spinner("Generating summary..."):
            max_n_pages = 1
            pdf_text = utils.extract_text_from_pdf(pdf_path, max_n_pages=max_n_pages)
            pdf_summary = get_summary(pdf_text)
            st.session_state.pdf_text[selected_pdf] = pdf_text
            st.session_state.pdf_summary[selected_pdf] = pdf_summary
    pdf_text = st.session_state.pdf_text[selected_pdf]
    pdf_summary = st.session_state.pdf_summary[selected_pdf]
    st.markdown(
        f"""
        ### Gemini's brief summary of the paper
        {pdf_summary}
        """
    )

    st.markdown("### Chat with Gemini about the paper")

    pre_message_prompt = get_pre_message_prompt(pdf_text, pdf_summary)

    if st.session_state["messages"] == []:
        st.session_state["messages"] = pre_message_prompt
    messages = st.session_state["messages"]

    chat_message = st.chat_input(
        """Ask Gemini Pro a question (Like "What do you think of the paper?")"""
    )

    # is_pirate = st.toggle("Chat with a pirate", False)
    # messages = make_pirate(messages, is_pirate=is_pirate)
    with st.container(height=600):
        if messages:
            write_messages_to_chat(messages)

        # When a message is sent, add it to the message history and get a response
        if chat_message:
            st.chat_message("user").markdown(chat_message)
            res_area = st.chat_message("assistant").empty()
            messages.append(
                {"role": "user", "parts": [chat_message]},
            )
            res_text = get_response(messages)
            res_area.markdown(res_text)
            messages.append({"role": "model", "parts": [res_text]})
        # TODO: create function write_to_chat
        # Use the write_to_chat function to hide the initial context?

    # with st.expander("debugging"):
    #    st.write(messages)  # Debugging

    return


if __name__ == "__main__":
    main()
