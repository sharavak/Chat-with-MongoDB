# 🛢️ Chat with MongoDB — Natural Language MongoDB Querying via LLM + Streamlit

An **AI-powered chatbot interface** that allows users to interact with a MongoDB database using natural language. This app uses **LangChain** and **GROQ API** to convert user queries into executable **MongoDB queries**, and displays the results in a user-friendly **Streamlit** interface.

[Live Demo on Streamlit Cloud](https://chat-with-db-101.streamlit.app/)

---

## Features

- 💬 **Conversational Chat with an Agent** to interact with MongoDB like you're talking to a data assistant.
- 🧠 **LLM-powered Query Understanding** using [GROQ API](https://groq.com/).
- 🗃️ **MongoDB Query Execution** from natural language (via PyMongo).
- 📚 **Contextual Memory** using LangChain's message history.
- 🚀 **Streamlit UI** with chat, code rendering, and real-time responses.
---

## Tech Stack

| Tool        | Purpose                                    |
|-------------|--------------------------------------------|
| [Streamlit](https://streamlit.io/) | Web UI for chat and interactivity          |
| [LangChain](https://www.langchain.com/) | Conversation memory, prompt management   |
| [GROQ API](https://groq.com/) | LLM for MongoDB query generation            |
| [MongoDB + PyMongo](https://www.mongodb.com/) | Query execution backend                  |
| Python      | Core development language                   |

---

## Installation

```bash
git clone https://github.com/sharavak/Chat-with-MongoDB.git
cd Chat-with-MongoDB
pip install -r requirements.txt
streamlit run streamlit_main.py
