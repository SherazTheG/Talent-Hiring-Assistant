# TalentScout AI Hiring Assistant

An intelligent chatbot designed to streamline the initial candidate screening process for a fictional recruitment agency, TalentScout. This application leverages a large language model (LLM) to gather essential candidate information and generate personalized, technical interview questions based on a candidate's declared skill set.

---

## Project Overview

The TalentScout AI Hiring Assistant guides a candidate through a series of questions to collect key details such as their name, contact information, years of experience, and desired position. The core functionality is the technical question generation, where the chatbot dynamically creates a set of 3-5 interview questions by prompting an LLM with the candidate's specified tech stack.

### Key Features
- A clean and intuitive web-based chat interface.
- Sequential information gathering with built-in validation.
- Dynamic, LLM-powered technical question generation.
- A robust fallback mechanism that generates questions locally if the LLM API is unavailable.
- Simulated, anonymized data storage to demonstrate secure handling of candidate information.
- Graceful session termination upon user request.

---

## Installation Instructions

1. Clone the repository:
    ```
    git clone <repository_link>
    cd talent_scout
    ```

2. Set up a virtual environment (recommended):
    ```
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install the required libraries:
    ```
    pip install streamlit requests
    ```

4. Configure API Key:  
   The application uses the OpenRouter API. You must set your API key as a Streamlit secret. Create a `.streamlit` folder in your project directory and a file named `secrets.toml` inside it.

   `.streamlit/secrets.toml`:
    ```
    OPENROUTER_API_KEY = "your_openrouter_api_key_here"
    ```

   You can get your API key by signing up for a free account at [https://openrouter.ai/](https://openrouter.ai/).

5. Run the application:
    ```
    streamlit run main.py
    ```

   The application will open in your default web browser.

---

## Usage Guide

- The chatbot will greet you and guide you through the screening process step-by-step.
- Enter your information in the text box as prompted.
- Press **Submit** to proceed to the next step.
- To end the conversation at any time, simply type `"exit"` or `"quit"`.
- Once all the required information is collected, the chatbot will display a summary and then generate a set of personalized technical questions.
- After the questions are displayed, the session will conclude, and your (anonymized) information will be saved to a local JSON file (`candidates_simulated.json`).

---

## Technical Details

- **Frontend:** Built using Streamlit, allowing rapid development of interactive web applications in Python.
- **Backend & Core Logic:** Written in Python.
- **Large Language Model (LLM):** Powered by the OpenRouter API. This serves as a unified interface to various LLMs, defaulting to meta-llama/llama-3.3-8b-instruct.
- **Prompt Engineering:** Strategically crafted prompts in `prompts.py` guide the LLM to provide concise, relevant outputs. These prompts handle greetings, contextual acknowledgments, and structured question generation.
- **Data Handling:** Candidate information is stored in a simple JSON file (`candidates_simulated.json`), mimicking a backend database. A basic anonymization technique masks sensitive data like emails and phone numbers before storage.

---

## Prompt Design

The prompt engineering in this project focuses on guiding the LLM to perform very specific, constrained tasks:

- **build_greeting_prompt():** Generates a warm and friendly greeting.
- **build_context_prompt():** Provides conversational context to generate brief, encouraging, 1-2 sentence responses maintaining the chat flow.
- **build_tech_questions_prompt():** The critical prompt that provides the candidate’s tech stack and instructions for generating a numbered list of 3-5 practical, conceptual, and troubleshooting technical questions.

---

## Challenges & Solutions

- **LLM Reliability:**  
  LLMs can sometimes produce unexpected or verbose responses.  
  *Solution:* Highly prescriptive prompts specifying length and format constraints.

- **API Downtime/Cost:**  
  Reliance on an external API is a single point of failure.  
  *Solution:* Local fallback mechanism (`safe_generate_questions_local`) using heuristics to generate relevant technical questions ensures continued functionality without API access.

- **Data Security:**  
  Storing sensitive Personally Identifiable Information (PII) in plain text is risky.  
  *Solution:* Simulated backend using a local JSON file with anonymization masking of emails and phone numbers to demonstrate data privacy best practices.

---
