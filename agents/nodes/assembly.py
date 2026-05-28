import os
import subprocess
import shutil
from state import AgentState
from settings import settings

async def assembly_node(state: AgentState):
    """
    Combines all updated sections and compiles the final PDF.
    """
    print("--- ASSEMBLING FINAL RESUME ---")
    
    # 1. Create a workspace for compilation
    build_dir = "build_temp"
    os.makedirs(build_dir, exist_ok=True)
    
    # 2. Copy the preamble and other static files
    preamble_path = settings.get_path("resumeSections", "preamble.tex")
    shutil.copy(preamble_path, build_dir)
    
    # 3. Copy the updated sections or fall back to originals if not updated
    sections = ["header", "objective", "summary", "skills", "experience1", "experience2", "education"]
    for section in sections:
        updated_path = settings.get_path("updatedResumeSections", f"{section}.tex")
        original_path = settings.get_path("resumeSections", f"{section}.tex")
        
        if os.path.exists(updated_path):
            shutil.copy(updated_path, os.path.join(build_dir, f"{section}.tex"))
        else:
            shutil.copy(original_path, os.path.join(build_dir, f"{section}.tex"))
            
    # 4. Prepare the main.tex for the build directory
    main_path = settings.get_path("resumeSections", "main.tex")
    shutil.copy(main_path, build_dir)
    
    # 5. Compile to PDF
    try:
        # Run pdflatex twice for references/links
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "main.tex"],
            cwd=build_dir,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "main.tex"],
            cwd=build_dir,
            check=True,
            capture_output=True
        )
        
        # 6. Move the final PDF to the output folder
        output_path = settings.get_path("output", "resume.pdf")
        shutil.move(os.path.join(build_dir, "main.pdf"), output_path)
        print(f"Success! Resume generated at {output_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during LaTeX compilation: {e.stderr.decode()}")
        raise e
    
    # 7. Cleanup
    shutil.rmtree(build_dir)
    # Clear the updatedResumeSections folder as requested
    updated_dir = settings.get_path("updatedResumeSections")
    for f in os.listdir(updated_dir):
        os.remove(os.path.join(updated_dir, f))
        
    return state
