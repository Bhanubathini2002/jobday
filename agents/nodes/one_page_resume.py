import os
from state import AgentState
from settings import settings
# pyrefly: ignore [missing-import]
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import subprocess
import traceback

async def one_page_resume_node(state: AgentState):
    """
    Agent that updates the One Page Resume based on the Job Description, Role, and Location.
    """
    print("--- UPDATING ONE PAGE RESUME ---")
    
    # 1. Read the original one-page resume
    resume_path = settings.get_path("resumeSections", "one page resume", "resume.tex")
    with open(resume_path, "r", encoding="utf-8") as f:
        original_resume = f.read()
    
    # 2. Get data from state
    user_data = state.get("user_data", {})
    job_description = user_data.get("job_description", "")
    role = user_data.get("role", "Target Role")
    location = user_data.get("location", "Target Location")
    
    # Initialize LLM
    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model="gpt-4o", 
        temperature=0.7,
    )

    # --- FIRST LLM CALL: EXTRACT KEYWORDS ---
    print("--- EXTRACTING KEYWORDS ---")
    extraction_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert technical recruiter. Your task is to extract the exact technical skills, tools, methodologies, and technologies required from the provided Job Description.\n"
                   "Output ONLY a comma-separated list of these keywords. Do not include any conversational filler."),
        ("user", "Job Description:\n{jd}\n\nPlease extract the keywords.")
    ])
    
    extraction_chain = extraction_prompt | llm
    extraction_response = await extraction_chain.ainvoke({"jd": job_description})
    extracted_keywords = extraction_response.content.strip()
    print("Extracted Keywords:", extracted_keywords)

    # --- SECOND LLM CALL: GENERATE RESUME ---
    print("--- GENERATING RESUME ---")
    resume_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert resume writer. Your task is to update a complete one-page LaTeX resume based on a Job Description, Role, Location, and a list of mandatory Keywords.\n\n"
                   "CRITICAL INSTRUCTIONS:\n"
                   "1. **Format:** Use the exact formatting, structure, and custom commands of the Original LaTeX Resume.\n"
                   "2. **Word Count:** Keep the word count strictly similar to the original to ensure it stays precisely on one page.\n"
                   "3. **Work Experience Formulation:** Rewrite work experience bullet points to follow this structure: 'what problem was solved', 'what was done', 'what was the impact', and MUST 'add specific metrics' (e.g., improved efficiency by 20%, reduced latency by 30ms).\n"
                   "4. **Semantic Keywords:** Semantically and meaningfully integrate the provided Keywords into EVERY section (Objective, Profile Summary, Technical Skills, Work Experience).\n"
                   "5. **Role & Location:** Prominently update the requested Role and Location in the header/objective. Ensure there are NO spelling mistakes.\n"
                   "6. **LaTeX Escaping:** ENSURE ALL SPECIAL CHARACTERS (e.g., &, %, $, #, _) are properly escaped in LaTeX (e.g., \\&, \\%, \\$, \\#, \\_). Failure to do so will break compilation.\n"
                   "7. Output ONLY the raw LaTeX code. Do NOT include markdown code blocks (e.g. ```latex) or any conversational filler.\n"
                   "8. If the Job Description is empty or invalid, return the Original LaTeX Resume EXACTLY as provided without any changes."),
        ("user", "Role: {role}\nLocation: {location}\nJob Description:\n{jd}\nMandatory Keywords to Include:\n{keywords}\n\nOriginal LaTeX Resume:\n{original}\n\nPlease provide the updated LaTeX code.")
    ])
    
    resume_chain = resume_prompt | llm
    resume_response = await resume_chain.ainvoke({
        "original": original_resume, 
        "jd": job_description,
        "role": role,
        "location": location,
        "keywords": extracted_keywords
    })

    updated_content = resume_response.content
    
    # Remove markdown code blocks if the LLM ignores instructions
    if updated_content.startswith("```latex"):
        updated_content = updated_content[8:]
    if updated_content.startswith("```"):
        updated_content = updated_content[3:]
    if updated_content.endswith("```"):
        updated_content = updated_content[:-3]
    updated_content = updated_content.strip()

    # Save to output_onepage folder
    output_dir = settings.get_path("output_onepage")
    os.makedirs(output_dir, exist_ok=True)
    
    updated_path = os.path.join(output_dir, "resume.tex")
    with open(updated_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
    
    # Compile LaTeX to PDF
    print("--- COMPILING ONE PAGE RESUME ---")
    try:
        process = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "resume.tex"],
            cwd=output_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if process.returncode == 0:
            print("Successfully compiled resume.pdf")
            # Cleanup temporary LaTeX files
            for ext in [".tex", ".aux", ".log", ".out"]:
                temp_file = os.path.join(output_dir, f"resume{ext}")
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        else:
            print("LaTeX Compilation Error:")
            print(process.stdout)
            print(process.stderr)
    except Exception as e:
        print(f"Failed to compile LaTeX: {type(e).__name__} - {e}")
        traceback.print_exc()
    
    # Update state
    if "resume_sections" not in state:
        state["resume_sections"] = {}
        
    state["resume_sections"]["one_page_resume"] = updated_content
    
    return state
