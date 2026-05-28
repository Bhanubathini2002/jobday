from state import AgentState
from settings import settings
# pyrefly: ignore [missing-import]
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


async def profile_summary_node(state: AgentState):
    """
    Agent that updates the Profile Summary section based on the Job Description.
    """
    print("--- UPDATING PROFILE SUMMARY ---")

    # 1. Read the original summary
    summary_path = settings.get_path("resumeSections", "summary.tex")
    with open(summary_path, "r", encoding="utf-8") as f:
        original_summary = f.read()

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
            "You are an expert resume writer specializing in professional profile summaries. "
            "Your task is to rewrite a LaTeX profile summary section so it aligns with the given Job Description. "
            "Maintain the EXACT same LaTeX formatting, commands, sections, vspace, bold text, and structure. "
            "Emphasize relevant skills, achievements, and domain expertise that match the JD. "
            "Keep it concise, impactful, and ATS-friendly.\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Output ONLY the raw LaTeX code.\n"
            "2. Do NOT include markdown code blocks (e.g. ```latex) or any conversational filler.\n"
            "3. If the Job Description is empty, invalid, or missing, return the Original LaTeX Section EXACTLY as provided without any changes or apologies."
        )),
        ("user", "Original LaTeX Section:\n{original}\n\nJob Description:\n{jd}\n\nPlease provide the updated LaTeX code.")
    ])

    chain = prompt | llm
    response = await chain.ainvoke({"original": original_summary, "jd": job_description})
    print("\n", response)

    updated_content = response.content

    # Save to updated folder
    updated_path = settings.get_path("updatedResumeSections", "summary.tex")
    with open(updated_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    # Update state
    state["resume_sections"]["profile_summary"] = updated_content

    return state
