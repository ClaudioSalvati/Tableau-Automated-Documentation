# base_dest_dir = r"<PATH>" # Path to base directory
# extracted_file = r"<PATH>.twb" # Path to the .twb file
# structure_XML = f"{base_dest_dir}\TWB_XML_structure.txt"

import xml.etree.ElementTree as ET

def extract_keys(elem, prefix='', keys_set=None):
    if keys_set is None:
        keys_set = set()
    
    for child in elem:
        new_key = f"{prefix}/{child.tag}"
        keys_set.add(new_key)
        extract_keys(child, new_key, keys_set)
        
    return keys_set

def convert_to_asterisk_representation(paths):
    output = []
    for path in paths:
        segments = path.split("/")
        asterisks = '*' * (len(segments) - 2)
        output_path = f"{asterisks} /{segments[-1]}"
        output.append(output_path)
    return output

def save_to_txt(lines, filename="output.txt"):
    with open(filename, "w") as f:
        for line in lines:
            f.write(line + "\n")

if __name__ == "__main__":
    # This variable is used in "01 Unzip TWBX file.py" 
    extracted_file = extracted_file

    # Parse the XML file
    tree = ET.parse(extracted_file)
    root = tree.getroot()

    xml_keys = sorted(extract_keys(root))
#    converted = convert_to_asterisk_representation(xml_keys)

    # Save the output to a text file
    save_to_txt(xml_keys, structure_XML)
    print(f"Data saved to {structure_XML}.")
