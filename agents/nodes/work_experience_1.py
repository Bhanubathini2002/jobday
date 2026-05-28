from state import AgentState
from settings import settings
# pyrefly: ignore [missing-import]
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


async def work_experience_1_node(state: AgentState):
    """
    Agent that updates Work Experience 1 section based on the Job Description.
    """
    print("--- UPDATING WORK EXPERIENCE 1 ---")

    # 1. Read the original experience
    exp_path = settings.get_path("resumeSections", "experience1.tex")
    with open(exp_path, "r", encoding="utf-8") as f:
        original_experience = f.read()

    # 2. Get Job Description from state
    job_description = state.get("user_data", {}).get("job_description", "")

    # Initialize LLM
    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model="gpt-4o",
        temperature=0.7,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an expert resume writer specializing in work experience sections. "
            "Your task is to rewrite a LaTeX work experience section so it aligns with the given Job Description. "
            "Maintain the EXACT same LaTeX formatting, commands, structure, company name, job title, and dates. "
            "Rewrite the bullet points to emphasize achievements, responsibilities, and technologies "
            "that are most relevant to the JD. Use strong action verbs and quantify impact where possible. "
            "Do NOT change the company name, job title, or employment dates.\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Output ONLY the raw LaTeX code.\n"
            "2. Do NOT include markdown code blocks (e.g. ```latex) or any conversational filler.\n"
            "3. If the Job Description is empty, invalid, or missing, return the Original LaTeX Section EXACTLY as provided without any changes or apologies."
        )),
        ("user", "Original LaTeX Section:\n{original}\n\nJob Description:\n{jd}\n\nPlease provide the updated LaTeX code.")
    ])

    chain = prompt | llm
    response = await chain.ainvoke({"original": original_experience, "jd": job_description})
    print("\n", response)

    updated_content = response.content

    # Save to updated folder
    updated_path = settings.get_path("updatedResumeSections", "experience1.tex")
    with open(updated_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    # Update state
    state["resume_sections"]["work_experience_1"] = updated_content

    return state
