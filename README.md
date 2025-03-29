# 🧠 LLM Code Tutor – AI-Powered Code Analysis and Learning Assistant

The **LLM Code Tutor** is an interactive AI-based application designed to help programming beginners understand and improve their Python code. Unlike traditional Large Language Models (LLMs) like ChatGPT that simply return a corrected version of your code, the LLM Code Tutor promotes **active learning** by guiding users through a structured review process.

Each aspect of the code – syntax, semantics, structure, style, efficiency, security, documentation, and best practices – is analyzed by specialized **Agents**. These agents combine objective Python analysis tools (e.g., Black, Bandit, Radon) with the natural language capabilities of a powerful LLM (**Qwen Coder 2.5 32B**) to generate helpful, explainable feedback.

---

## 🔧 Features

- Modular agent-based architecture
- Iterative, interactive feedback loop
- No automatic code correction – promotes understanding
- Agent support for:
  - Syntax
  - Semantics
  - Code Style
  - Code Structure
  - Security
  - Efficiency
  - Documentation
  - Error Handling
  - Best Practices
- Integration with [Qwen Coder 2.5 32B](https://huggingface.co/spaces/Qwen/Qwen2.5-Coder-demo) via Hugging Face Spaces

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/SimeonSimeonov24/LLM-Code-Tutor.git
cd LLM-Code-Tutor
```

### 2. Install dependencies

Make sure you have Python 3.10+ installed, then run:

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root and add the following:

```
CLIENT_URL=<URL to the Qwen Coder API or your model backend>
```

> The system currently uses Qwen Coder 2.5 32B hosted at Hugging Face:  
> [https://huggingface.co/spaces/Qwen/Qwen2.5-Coder-demo](https://huggingface.co/spaces/Qwen/Qwen2.5-Coder-demo)
> It is queried through a Gradio Client


### 4. Run the application

Start the Streamlit app:

```bash
streamlit run app.py
```

The interface will open in your browser, allowing you to input Python code and receive guided, step-by-step analysis through the Code Tutor.

---

## 👨‍🎓 Project Authors

Developed as part of a university software engineering project by:

- Simeon Simeonov  
- Mohannad Al Turk