# 🤖 PaperFast

PaperFast is an AI-powered application designed to accelerate your paper research and study process. It leverages a team of intelligent agents to assist you in searching for, summarizing, and organizing academic papers, specifically from Arxiv.

## ✨ Features

*   **Multi-Agent Workflow**: Utilizes LangGraph to orchestrate specialized agents (Search, Summary, etc.) for complex tasks.
*   **Paper Search**: Efficiently searches for relevant papers using the Arxiv API.
*   **Interactive Chat Interface**: Built with Streamlit for a user-friendly, chat-based experience.
*   **Traceability**: Integrated with LangFuse for monitoring and tracing agent interactions.

## 🛠️ Tech Stack

*   **Python 3.12+**
*   **Streamlit**: For the web interface.
*   **LangChain & LangGraph**: For building the agentic workflow.
*   **UV**: For fast Python package management.
*   **MCP (Model Context Protocol)**: For standardized tool integration.

## 🚀 Getting Started

### Prerequisites

*   Python 3.12 or higher
*   [uv](https://github.com/astral-sh/uv) (recommended for dependency management)

### Installation

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd PaperFast
    ```

2.  **Install dependencies**
    ```bash
    uv sync
    ```

3.  **Set up MCP Server**
    For local MCP setup, you need to install the Arxiv MCP server tool:
    ```bash
    uv tool install arxiv-mcp-server
    ```

4.  **Environment Setup**
    Create a `.env` file in the root directory and add your necessary API keys (e.g., OpenAI, LangFuse). You can use `.env.example` as a reference if available.
    ```env
    OPENAI_API_KEY=your_api_key_here
    LANGFUSE_SECRET_KEY=your_langfuse_secret_key
    LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
    LANGFUSE_HOST="https://cloud.langfuse.com"
    ```

### Running the Application

You can start the application using `poe` (if configured) or directly with Streamlit.

**Using poe:**
```bash
poe run
```

**Using streamlit directly:**
```bash
streamlit run app/main.py
```

## 📂 Project Structure

*   `app/`: Main application source code.
    *   `main.py`: Entry point for the Streamlit app.
    *   `workflow/`: Contains the LangGraph workflow and agent definitions.
        *   `agents/`: Individual agent implementations (Search, Master, etc.).
*   `pyproject.toml`: Project configuration and dependencies.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
