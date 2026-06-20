# pyrefly: ignore [missing-import]
from langchain_text_splitters import RecursiveCharacterTextSplitter

def get_text_splitter():
    """ create chunk splitter"""

    return RecursiveCharacterTextSplitter(
       chunk_size=1000,
       chunk_overlap=200

    )
def chunk_repository_files(
        repo_id:int,
        parsed_files:list
):
    """ splits parsed files into chunk
    """
    splitter=get_text_splitter()

    all_chunks=[]

    for parsed_file in parsed_files:
        file_path=parsed_file['file_path']
        language=parsed_file['language']
        content=parsed_file['content']

        chunks = splitter.split_text(
            content
        )
        for chunk in chunks:
            all_chunks.append(
                {
                    "repo_id": repo_id,
                    "file_path": file_path,
                    "language": language,
                    "chunk_text": chunk
                }
            )
    return all_chunks