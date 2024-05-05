# pylint: disable=invalid-name
"""Page for streamlit app"""

import streamlit as st
import pyprojroot
import sys
import google.generativeai as genai

from datetime import date

import Home

sys.path.insert(0, str(pyprojroot.here()))  # Add parent directory to path
from src import utils  # pylint: disable=wrong-import-position

import arxiv


# @st.cache_resource
def get_new_uploads(n_papers=2, query="cat:cs.LG"):
    """Get new papers uploaded to arXiv
    Computer science: Machine Learning = cs.LG
    Other,
    - Statistics: Machine Learning = stat.ML
    - Computer science: Artificial Intelligence = cs.AIs
    - Computer science: Neural and Evolutionary Computing = cs.NE
    - Computer science: Systems and Control = cs.SY
    - Math: Optimization and Control = math.OC
    """
    arxiv_client = utils.arxiv.Client()
    search_query = arxiv.Search(
        query=query,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        max_results=n_papers,
    )
    new_papers = arxiv_client.results(search_query)
    return new_papers


# @st.cache_resource
def get_arxiv_query_text(_new_paper_summaries):
    """Get the text of the arXiv query"""
    output_text = ""
    for r in _new_paper_summaries:
        authors = ", ".join([a.name for a in r.authors])
        output_text += f"**Title:** {r.title}.  \n"
        output_text += f"**Authors:** {authors}.  \n"
        output_text += f"**Published:** {r.published}.  \n"
        output_text += f"**Abstract:** {r.summary}  \n"
        output_text += "\n"
    return output_text


def print_arxiv_query(new_paper_summaries):
    # Print the text
    output = new_paper_summaries
    # output = output.replace("**Title:** ", "--- \n ##### ")
    output = output.replace("--- \n", "", 1)
    st.markdown(output)
    return


def get_summary_response(
    new_paper_summaries, model=Home.DEFAULT_MODEL, safety_settings=None
):
    """Get the summary response"""
    if safety_settings is None:
        safety_settings = Home.DEFAULT_SAFETY_SETTINGS
    prompt = f"""
        Below are the summaries of the most recent papers uploaded to arXiv.
        Summarize the general conclusions that an ML researcher should take away:
        - What are the important things that they should know?
        - What are the key results?
        - Do the results seem like they will be impactful?

        ---
        {new_paper_summaries}
        ---
        """
    model = genai.GenerativeModel(model)
    response = model.generate_content(prompt, safety_settings=safety_settings)
    return response.text


def main():

    # Intro:
    st.title("Summary of recent arXiv papers")
    st.write(
        """
        Select a category and Gemini will summarize the most recently uploaded
        arXiv papers on that topic.
        """
    )

    available_topics = {
        "Machine Learning": "cat:cs.LG",
        "Artificial Intelligence": "cat:cs.AI",
        "Neural and Evolutionary Computing": "cat:cs.NE",
        "Systems and Control": "cat:cs.SY",
        "Optimization and Control": "cat:math.OC",
    }
    # Drop-down to select topic
    selected_topic = st.selectbox(
        "Select a topic",
        list(available_topics.keys()),
        index=0,
    )
    query = available_topics[selected_topic]

    n_papers = st.number_input(
        "Number of most recent papers to summarize", value=2, min_value=1, max_value=10
    )
    # day = st.date_input(
    #    "Select a day (not implemented yet)", value="today", max_value=date.today()
    # )
    # new_papers =
    # new_paper_summaries = get_arxiv_query_text(new_papers)
    new_paper_summaries = get_arxiv_query_text(
        get_new_uploads(n_papers=n_papers, query=query)
    )
    st.divider()

    # Papers:
    # st.write(f"Summarizing papers from {day}")
    st.write("### Retrieved papers")
    # Print the query
    # TODO switch from scrolling container to something that lets you select 1 paper at a time?
    with st.container(height=600, border=True):
        print_arxiv_query(new_paper_summaries)
    st.divider()

    # Summary:
    st.markdown("### Gemini's summary")
    # TODO switch from spinner to streaming response
    with st.spinner("Summarizing papers..."):
        model_summary = get_summary_response(new_paper_summaries)
    st.write(model_summary)
    st.divider()

    return


if __name__ == "__main__":
    main()
