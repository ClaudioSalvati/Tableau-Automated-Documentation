zip_filepath = r"<PATH>" # Path to the twbx file
base_dest_dir = r">PATH>" # Path to the output directory
file_extension = ".twb"
structure_XML = f"{base_dest_dir}\TWB_XML_structure.txt" # Output file for the XML structure

import zipfile
import os

def unzip_specific_file(zip_filepath, dest_dir, file_extension):
    """
    Unzips a specific file (with given extension) from the zip file into a directory with the same name as the zip file.
    Returns the full path to the unzipped file.

    :param zip_filepath: Path to the .zip file.
    :param dest_dir: Base destination directory where a new folder will be created.
    :param file_extension: The file extension of the file to extract.
    :return: Full path to the extracted file.
    """
    # Derive the folder name from the .zip filename
    folder_name = os.path.splitext(os.path.basename(zip_filepath))[0]
    full_dest_dir = os.path.join(dest_dir, folder_name)

    # Check if folder exists. If not, create it.
    if not os.path.exists(full_dest_dir):
        os.makedirs(full_dest_dir)

    extracted_file_path = None
    try:
        with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
            for file in zip_ref.namelist():
                if file.endswith(file_extension):
                    zip_ref.extract(file, full_dest_dir)
                    extracted_file_path = os.path.join(full_dest_dir, file)
                    break
    except Exception as e:
        print(f"An error occurred: {e}")

    return extracted_file_path

extracted_file = unzip_specific_file(zip_filepath, base_dest_dir, file_extension)
if extracted_file:
    print(f"Extracted file: {extracted_file}")
else:
    print("No .twb file found in the archive.")
