# arxiv-chat

Chat with arXiv papers.

## References

- [Gemini API docs](https://ai.google.dev/gemini-api/docs/get-started/python)
- [Monitor Google API traffic](https://console.cloud.google.com/apis/dashboard)

## Roadmap

Primary:

- [x] Create a Streamlit app
- [x] Integrate with Gemini API
- [x] Add local PDFs of important papers
- [x] Enable chat with local papers (simple text context)
- [ ] Add option to get selected papers from arXiv
- [ ] In second page, show LLM summary/evaluations of this day's/week's papers
  - Get most recent papers, summarize them, evalute them, rank them by importance
- [ ] Use RAG with a database for better summaries/chat responses

Secondary:

- [ ] Work on prompt engineering for better summaries/chat responses
- [ ] Enable users to select a model personality (choose personality from drop down, which corresponds to a specific prompt or fine-tuned model)
- [ ] Fine-tune a model for summaries and paper evaluation
- [ ] Fine-tune a silly model (e.g. always answer in rhymes)

Miscellaneous:

- [ ] Validate LLM summaries/evaluations with Pydantic
- [ ] Add CI/CD with GitHub Actions, pytest, and Docker
- [ ] Embed in jbreffle.github.io
- [ ] Add annotations to pdf based on LLM summaries/chat responses
- [ ] Add option for users to provide their own API key and select model to use (e.g. allow gemini-1.5-pro only for user-provided keys)
- [ ] Add option for users to easily run the app locally with a custom LLM?
