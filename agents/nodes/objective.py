import os
from state import AgentState
from settings import settings
# pyrefly: ignore [missing-import]
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

async def objective_node(state: AgentState):
    """
    Agent that updates the Objective section based on the Job Description.
    """
    print("--- UPDATING OBJECTIVE ---")
    
    # 1. Read the original objective
    obj_path = settings.get_path("resumeSections", "objective.tex")
    with open(obj_path, "r", encoding="utf-8") as f:
        original_objective = f.read()
    
    # 2. Get Job Description from state
    job_description = state.get("user_data", {}).get("job_description", "")
    print(job_description)

    # Initialize LLM (Standard OpenAI)
    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model="gpt-4o", # You can change this to your preferred model
        temperature=0.7,
    )

    # Alternative: Azure OpenAI (Commented out)
    # llm = AzureChatOpenAI(
    #     azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    #     azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
    #     openai_api_key=settings.AZURE_OPENAI_API_KEY,
    #     openai_api_version=settings.AZURE_OPENAI_API_VERSION,
    #     temperature=0.7,
    # )
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert resume writer. Your task is to update a LaTeX resume section based on a Job Description. Maintain the exact same LaTeX formatting, including sections, vspace, and bold text. ONLY rewrite the content to better align with the job. \n\nCRITICAL INSTRUCTIONS:\n1. Output ONLY the raw LaTeX code.\n2. Do NOT include markdown code blocks (e.g. ```latex) or any conversational filler (e.g. 'Here is the updated...').\n3. If the Job Description is empty, invalid, or missing, return the Original LaTeX Section EXACTLY as provided without any changes or apologies."),
        ("user", "Original LaTeX Section:\n{original}\n\nJob Description:\n{jd}\n\nPlease provide the updated LaTeX code.")
    ])
    
    chain = prompt | llm
    response = await chain.ainvoke({"original": original_objective, "jd": job_description})
    print("/n",response)


    
    updated_content = response.content
    # 4. Save to temporary folder
    updated_path = settings.get_path("updatedResumeSections", "objective.tex")
    with open(updated_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
    
    # 5. Update state
    state["resume_sections"]["objective"] = updated_content
    
    return state
