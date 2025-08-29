"""
Prompt engineering module for TalentScout Hiring Assistant (refined)
Contains prompt builders used by the chatbot for different interactions.
All prompts are concise and designed to produce useful model output.
"""

def build_greeting_prompt():
    """
    Build greeting prompt for initial interaction.
    Kept short and professional.
    """
    return (
        "You are TalentScout's AI Hiring Assistant. "
        "Greet the candidate warmly and explain that you will collect basic information "
        "and generate technical questions based on their tech stack. Keep it friendly and under 3 sentences."
    )


def build_tech_questions_prompt(tech_stack: str):
    """
    Build a prompt asking the LLM to generate 3-5 technical interview questions
    for the given tech stack. The prompt asks for a mix of conceptual and practical questions.
    """
    return (
        f"Generate 3-5 technical interview questions for a candidate with the following tech stack: {tech_stack}\n\n"
        "Requirements:\n"
        "- Practical, real-world focused questions\n"
        "- Mix of conceptual and hands-on / troubleshooting prompts\n"
        "- Moderate difficulty (suitable for initial technical screening)\n"
        "- Cover multiple facets of the technologies mentioned (architecture, debugging, best-practices)\n"
        "- Format as a numbered list (1., 2., ...). Keep each question concise."
    )


def build_context_prompt(step: str, user_input: str):
    """
    Build contextual replies for specific steps (name, experience, position).
    These are small prompts for the assistant to provide encouraging acknowledgements.
    """
    prompts = {
        "fullname": f"Acknowledge the candidate's name '{user_input}' and provide a brief encouraging transition to the next question.",
        "experience": f"The candidate has {user_input} years of experience. Provide a brief, positive acknowledgment before moving forward.",
        "position": f"The candidate is applying for: {user_input}. Acknowledge this and show enthusiasm about their interest."
    }
    return prompts.get(step, f"Acknowledge the user's input: {user_input}")


def build_fallback_prompt(user_input: str, current_step: str):
    """
    Prompt used when candidate input is unexpected. Short and warm redirection.
    """
    return (
        f'A candidate in a hiring session said: "{user_input}"\n\n'
        f"Current step: {current_step}\n\n"
        "Provide a helpful, friendly response that: 1) acknowledges input, 2) redirects back to the process, "
        "3) clarifies what information is needed next. Keep response under 2 sentences."
    )


def build_validation_error_prompt(step: str, error_type: str):
    """
    Returns validation-error messages for the UI to display (not sent to model).
    """
    prompts = {
        "email": "I need a valid email address to contact you later. Please provide an email in the format: name@domain.com",
        "phone": "Please provide a valid phone number (7-15 digits). You can include country code if needed.",
        "experience": "Please enter your years of experience as a number (for example: 3, 5.5, or 0 for fresh graduate)",
        "required": f"This information is required for the screening process. Could you please provide your {step}?"
    }
    return prompts.get(error_type, "Please provide the requested information to continue.")


def build_question_analysis_prompt(question: str, user_answer: str, tech_stack: str):
    """
    Build a prompt designed to assess a candidate's answer to a technical question.
    Model should return a short structured assessment.
    """
    return (
        "Analyze this technical interview response and provide a concise assessment:\n\n"
        f"Question: {question}\n"
        f"Candidate's Answer: {user_answer}\n"
        f"Candidate's Tech Stack: {tech_stack}\n\n"
        "Return a short assessment including:\n"
        "1) Technical accuracy (brief)\n"
        "2) Depth of knowledge\n"
        "3) Suggested follow-up questions (1-2)\n"
        "4) Overall rating on a 1-5 scale\n\nKeep the response professional and constructive."
    )


def build_summary_prompt(candidate_info: dict):
    """
    Build prompt for generating a final candidate summary if we want a model-generated summary.
    """
    name = candidate_info.get("fullname", "Not provided")
    email = candidate_info.get("email", "Not provided")
    phone = candidate_info.get("phone", "Not provided")
    experience = candidate_info.get("experience", "Not provided")
    position = candidate_info.get("position", "Not provided")
    location = candidate_info.get("location", "Not provided")
    techstack = candidate_info.get("techstack", "Not provided")

    return (
        f"Create a concise professional summary for the hiring team using the details below:\n\n"
        f"Name: {name}\nEmail: {email}\nPhone: {phone}\nExperience: {experience} years\n"
        f"Position: {position}\nLocation: {location}\nTech Stack: {techstack}\n\n"
        "Highlight key qualifications, technical strengths, short recommended next steps, and a suitability score (1-5). "
        "Keep it short (4-6 sentences)."
    )
