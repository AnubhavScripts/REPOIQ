import os
SUPPORTED_EXTENSIONS={
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".java": "java",
    ".go": "go",
    ".cpp": "cpp",
    ".c": "c"
}

IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "__pycache__",
    ".next",
    "dist",
    "build",
    "venv"
}
def is_valid_code_file(file_name:str)-> bool:
    """ check if file extension is valid"""
    extension= os.path.splitext(file_name)[1]
    return extension in SUPPORTED_EXTENSIONS

def detect_language(file_name :str) -> str:
    """Detect Programming Lang from extension"""

    extension=os.path.splitext(file_name)[1]
    return SUPPORTED_EXTENSIONS.get(extension,"unknown")

def parse_repository(local_path: str):
    """
    Walk repository and return parsed code files
    """
    parsed_files = []

    for root,dirs,files in os.walk(local_path):
     dirs[:]=[
        d for d in dirs
        if d not in IGNORED_DIRECTORIES
    ]
    for file in files:
        if not is_valid_code_file(file):
            continue
        full_path = os.path.join(
                root,
                file
            )
        relative_path=os.path.relpath(
        full_path,local_path
         )
        language=detect_language(file)

        try:
          
          with open ( #opens the file
            full_path,
            "r",#read mode on
            encoding="utf-8", # read the text as utf-8 ,followed by most code files
            errors="ignore"
            ) as f: # creates a file object
           
           content=f.read()

           parsed_files.append(
               {
                   "file_path": relative_path,
                   "language" : language,
                   "content":content
               }
        )
        except Exception as e:
           print(f"Failed to read {full_path}: {e}")
           continue


    return parsed_files 
           