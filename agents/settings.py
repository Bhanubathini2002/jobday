import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.ROOT_DIR = os.getenv("ROOT_DIR", "")
        
        if not self.ROOT_DIR:
            # Calculate absolute path to the resume root (one level up from agents/)
            self.ROOT_DIR = str(Path(__file__).resolve().parent.parent)
        
        self.ROOT_DIR = str(Path(self.ROOT_DIR).resolve())
        print(f"DEBUG: Settings initialized. ROOT_DIR: {self.ROOT_DIR}", flush=True)

    def get_path(self, *path_parts):
        res = str(Path(self.ROOT_DIR).joinpath(*path_parts))
        # print(f"DEBUG: get_path({path_parts}) -> {res}", flush=True)
        return res

settings = Settings()
