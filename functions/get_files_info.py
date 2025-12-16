import os


def get_files_info(working_directory, directory="."):
    if not os.path.isabs(working_directory):
        if not os.path.exists(os.path.abspath(working_directory)):
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            potential_path = os.path.join(project_root, working_directory)
            if os.path.exists(potential_path):
                working_directory = potential_path

    working_directory = os.path.abspath(working_directory)
    target_dir = os.path.normpath(os.path.join(working_directory, directory))

    # Will be True or False
    valid_target_dir = (
        os.path.commonpath([working_directory, target_dir]) == working_directory
    )

    if not valid_target_dir:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    if not os.path.isdir(target_dir):
        return f'Error: "{directory}" is not a directory'

    list_of_entries = os.listdir(target_dir)
    results = []

    for entry in list_of_entries:
        try:
            entry_path = os.path.join(target_dir, entry)
            is_dir = os.path.isdir(entry_path)
            file_size = os.path.getsize(entry_path)
            results.append(f"- {entry}: file_size={file_size} bytes, is_dir={is_dir}")
        except Exception:
            results.append(f"Error: {entry}: could not retrieve info")

    return "\n".join(results)
