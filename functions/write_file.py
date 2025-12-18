import os
from google.genai import types


def write_file(working_directory, file_path, content):
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

    if os.path.isdir(target_file):
        return f'Error: Cannot write to "{file_path}" as it is a directory'

    os.makedirs(os.path.dirname(target_file), exist_ok=True)

    try:
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)
        return (
            f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        )
    except Exception as e:
        return f'Error: Could not write file "{file_path}": {str(e)}'


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a specified file relative to the working directory, creating directories as needed",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to write content to, relative to the working directory",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content to write to the file",
            ),
        },
    ),
)
