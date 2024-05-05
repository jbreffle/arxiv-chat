"""Utility functions for the project."""

import pyprojroot
import os
import urllib.request
import arxiv
from pypdf import PdfReader

PDF_DIR = pyprojroot.here("data")

# Make sure the data directory exists
os.makedirs(PDF_DIR, exist_ok=True)

local_papers = {
    "paper_1": {
        "title": "Attention is All You Need",
        "arxiv_id": "1706.03762",
        "filename": "vaswani_et_al_2017.pdf",
    },
    "paper_2": {
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "arxiv_id": "1810.04805",
        "filename": "devlin_et_al_2018.pdf",
    },
    "paper_3": {
        "title": "Generative Adversarial Nets",
        "arxiv_id": "1406.2661",
        "filename": "goodfellow_et_al_2014.pdf",
    },
    "paper_4": {
        "title": "Playing Atari with Deep Reinforcement Learning",
        "arxiv_id": "1312.5602",
        "filename": "mnih_et_al_2013.pdf",
    },
    "paper_5": {
        "title": "ImageNet Classification with Deep Convolutional Neural Networks",
        "arxiv_id": "",
        "alt_url": "https://proceedings.neurips.cc/paper_files/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf",
        "filename": "krizhevsky_et_al_2012.pdf",
    },
}


def get_local_papers(papers=None, silent=False):
    """Download select papers"""
    if papers is None:
        papers = local_papers
    arxiv_client = arxiv.Client()
    for paper in papers.values():
        # Check if the paper has been downloaded
        if not os.path.exists(os.path.join(PDF_DIR, paper["filename"])):
            if not silent:
                print(f"Downloading: {paper['filename']} to {PDF_DIR}")
            if paper["arxiv_id"] == "":
                urllib.request.urlretrieve(
                    paper["alt_url"], os.path.join(PDF_DIR, paper["filename"])
                )
            else:
                search_by_id = arxiv.Search(id_list=[paper["arxiv_id"]])
                paper_info = next(arxiv_client.results(search_by_id))
                paper_info.download_pdf(dirpath=PDF_DIR, filename=paper["filename"])
        else:
            if not silent:
                print(f"Already downloaded: {paper['title']}")
    return


def extract_text_from_pdf(pdf_path, max_n_pages=None):
    reader = PdfReader(pdf_path)
    text = ""
    for i, page in enumerate(reader.pages):
        if max_n_pages is not None and i > max_n_pages:
            break
        text += page.extract_text()
    return text
