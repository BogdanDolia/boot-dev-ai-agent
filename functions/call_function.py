import google.genai.types as types
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ],
)

# Mapping of function names to their module and function
FUNCTION_MAP = {
    "get_files_info": ("functions.get_files_info", "get_files_info"),
    "get_file_content": ("functions.get_file_content", "get_file_content"),
    "run_python_file": ("functions.run_python_file", "run_python_file"),
    "write_file": ("functions.write_file", "write_file"),
}


def call_function(function_call, verbose=False):
    try:
        if verbose:
            print(f"Calling function: {function_call.name}({function_call.args})")
        else:
            print(f" - Calling function: {function_call.name}")
    except Exception as e:
        print(f"Error printing function call info: {e}")

    function_result = ""

    # Dynamically import and call the function
    try:
        if function_call.name in FUNCTION_MAP:
            try:
                module_path, function_name = FUNCTION_MAP[function_call.name]
                module = __import__(module_path, fromlist=[function_name])
                func = getattr(module, function_name)
            except ImportError as e:
                return types.Content(
                    role="tool",
                    parts=[
                        types.Part.from_function_response(
                            name=function_call.name,
                            response={"error": f"Failed to import module: {str(e)}"},
                        )
                    ],
                )
            except AttributeError as e:
                return types.Content(
                    role="tool",
                    parts=[
                        types.Part.from_function_response(
                            name=function_call.name,
                            response={"error": f"Function not found in module: {str(e)}"},
                        )
                    ],
                )

            # Prepare arguments - all functions require working_directory as first param
            # If not provided in args, default to current directory
            try:
                if isinstance(function_call.args, dict):
                    args_dict = dict(function_call.args)
                    # Inject working_directory if not present (for security, default to ".")
                    if "working_directory" not in args_dict:
                        args_dict["working_directory"] = "./calculator"
                    function_result = func(**args_dict)
                else:
                    # If args is not a dict, treat it as working_directory
                    function_result = func(function_call.args)
            except TypeError as e:
                return types.Content(
                    role="tool",
                    parts=[
                        types.Part.from_function_response(
                            name=function_call.name,
                            response={"error": f"Invalid arguments: {str(e)}"},
                        )
                    ],
                )
            except Exception as e:
                return types.Content(
                    role="tool",
                    parts=[
                        types.Part.from_function_response(
                            name=function_call.name,
                            response={"error": f"Function execution error: {str(e)}"},
                        )
                    ],
                )
        else:
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_call.name,
                        response={"error": f"Unknown function: {function_call.name}"},
                    )
                ],
            )
    except Exception as e:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call.name,
                    response={"error": f"Unexpected error: {str(e)}"},
                )
            ],
        )

    try:
        return types.Content(
            role="user",
            parts=[
                types.Part.from_function_response(
                    name=function_call.name,
                    response={"result": function_result},
                )
            ],
        )
    except Exception as e:
        # Fallback error response if we can't create the proper response
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call.name,
                    response={"error": f"Failed to create response: {str(e)}"},
                )
            ],
        )
