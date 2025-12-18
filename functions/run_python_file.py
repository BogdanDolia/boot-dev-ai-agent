import os
import subprocess
from google.genai import types


def run_python_file(working_directory, file_path, args=None):
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
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(target_file):
        return f'Error: "{file_path}" does not exist or is not a regular file'

    if not target_file.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file'

    command = ["python", target_file]

    command.extend(args or [])

    try:
        result = subprocess.run(
            command,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return f"Process exited with code {result.returncode}"

        if not result.stdout and not result.stderr:
            return "No output produced"

        if result.stdout and result.stderr:
            return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

        if result.stdout or result.stderr:
            return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except Exception as e:
        return f"Error: executing Python file: {e}"


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a specified Python file relative to the working directory with optional arguments and captures its output",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Python file path to run, relative to the working directory",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Optional arguments to pass to the Python file",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
    ),
)
