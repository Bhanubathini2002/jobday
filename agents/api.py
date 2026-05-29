from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from settings import settings
from graphs.resume_graph import resume_graph
from nodes.one_page_resume import one_page_resume_node

app = FastAPI(title="Agentic Resume Builder API")

# Configure CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResumeRequest(BaseModel):
    job_description: str

class OnePageResumeRequest(BaseModel):
    job_description: str
    role: str
    location: str

@app.get("/")
async def root():
    return {"message": "Agentic Resume Builder API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}

# Trigger the actual agent logic
@app.post("/generate-section/{section_id}")
async def generate_section(section_id: str, request: ResumeRequest):
    """
    Triggers the agentic workflow to update a specific section.
    """
    if section_id != "objective":
        raise HTTPException(status_code=400, detail="Only 'objective' section is currently supported.")

    # Initialize the state
    initial_state = {
        "user_data": {"job_description": request.job_description},
        "resume_sections": {},
        "messages": []
    }

    try:
        # Invoke the graph
        result = await resume_graph.ainvoke(initial_state)
        
        return {
            "section": section_id,
            "status": "success",
            "message": f"Successfully updated {section_id} section.",
            "updated_content": result["resume_sections"].get(section_id, "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-one-page")
async def generate_one_page(
    job_description: str = Form(...),
    role: str = Form(...),
    location: str = Form(...)
):
    """
    Triggers the one-page resume node directly.
    """
    initial_state = {
        "user_data": {
            "job_description": job_description,
            "role": role,
            "location": location
        },
        "resume_sections": {},
        "messages": []
    }

    try:
        result = await one_page_resume_node(initial_state)
        
        return {
            "status": "success",
            "message": "Successfully updated one page resume.",
            "updated_content": result["resume_sections"].get("one_page_resume", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8080, reload=True)
