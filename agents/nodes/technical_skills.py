from state import AgentState
from settings import settings
# pyrefly: ignore [missing-import]
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


async def technical_skills_node(state: AgentState):
    """
    Agent that updates the Technical Skills section based on the Job Description.
    """
    print("--- UPDATING TECHNICAL SKILLS ---")

    # 1. Read the original skills
    skills_path = settings.get_path("resumeSections", "skills.tex")
    with open(skills_path, "r", encoding="utf-8") as f:
        original_skills = f.read()

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
            "You are an expert resume writer specializing in technical skills sections. "
            "Your task is to update a LaTeX technical skills section to best align with the given Job Description. "
            "Maintain the EXACT same LaTeX formatting, commands, structure, and category groupings. "
            "Prioritize and reorder skills that are most relevant to the JD. "
            "You may add highly relevant skills the candidate likely possesses based on context, "
            "but do NOT fabricate unrelated skills. Remove or de-prioritize less relevant ones.\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Output ONLY the raw LaTeX code.\n"
            "2. Do NOT include markdown code blocks (e.g. ```latex) or any conversational filler.\n"
            "3. If the Job Description is empty, invalid, or missing, return the Original LaTeX Section EXACTLY as provided without any changes or apologies."
        )),
        ("user", "Original LaTeX Section:\n{original}\n\nJob Description:\n{jd}\n\nPlease provide the updated LaTeX code.")
    ])

    chain = prompt | llm
    response = await chain.ainvoke({"original": original_skills, "jd": job_description})
    print("\n", response)

    updated_content = response.content

    # Save to updated folder
    updated_path = settings.get_path("updatedResumeSections", "skills.tex")
    with open(updated_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    # Update state
    state["resume_sections"]["technical_skills"] = updated_content

    return state
