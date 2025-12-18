import os
import sys
import google.genai.types as types

# Add parent directory to path to allow importing config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MAX_CHARS


def get_file_content(working_directory, file_path):
    if not os.path.isabs(working_directory):
        if not os.path.exists(os.path.abspath(working_directory)):
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            potential_path = os.path.join(project_root, working_directory)
            if os.path.exists(potential_path):
                working_directory = potential_path

    working_directory = os.path.abspath(working_directory)
    target_file = os.path.normpath(os.path.join(working_directory, file_path))

    # Will be True or False
    valid_target_file = (
        os.path.commonpath([working_directory, target_file]) == working_directory
    )

    if not valid_target_file:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(target_file):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read(MAX_CHARS)  # Limit to first 10,000 characters
            if f.read(1):
                content += (
                    f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
                )
        return content
    except Exception as e:
        return f'Error: Could not read file "{file_path}": {str(e)}'


schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Gets the content of a specified file relative to the working directory, limited to the first 10,000 characters",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to get content from, relative to the working directory",
            ),
        },
    ),
)
