import xml.etree.ElementTree as ET
import csv
import pandas as pd

# Constants
BASE_DEST_DIR = r"<PATH>" # Path to your base directory
UTF8 = "utf-8"

def process_calculated_fields(root, csv_file_path):
    processed_data = set()
    with open(csv_file_path, 'w', newline='') as csvfile:
        fieldnames = ['Datasource Detail', 'Caption', 'Datatype', 'Name', 'Role', 'Type', 'Value', 'Hidden', 'Domain Type', 'Member Values', 'Calculation Formula']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for datasource in root.findall('.//datasource'):
            ds_caption = datasource.attrib.get('caption', '')
            ds_name = datasource.attrib.get('name', '')
            ds_detail = ds_caption if ds_caption else ds_name
            for column in datasource.findall('.//column'):
                members = column.findall('members/member')
                member_values = []
                for member in members:
                    alias = member.attrib.get('alias', '')
                    value = member.attrib.get('value', '')
                    if alias:
                        member_values.append(f"{value} ({alias})")
                    else:
                        member_values.append(value)
                member_values_str = ", ".join(member_values)
                calculation_formula = ''
                if ds_name != 'Parameters':
                    calculation = column.find('calculation')
                    if calculation is not None:
                        calculation_formula = calculation.attrib.get('formula', '')
                data = {
                    'Datasource Detail': ds_detail,
                    'Caption': column.attrib.get('caption', ''),
                    'Datatype': column.attrib.get('datatype', ''),
                    'Name': column.attrib.get('name', ''),
                    'Role': column.attrib.get('role', ''),
                    'Type': column.attrib.get('type', ''),
                    'Value': column.attrib.get('value', ''),
                    'Hidden': column.attrib.get('hidden', ''),
                    'Domain Type': column.attrib.get('param-domain-type', ''),
                    'Member Values': member_values_str,
                    'Calculation Formula': calculation_formula
                }
                tuple_data = tuple(data.items())
                if tuple_data not in processed_data:
                    processed_data.add(tuple_data)
                    writer.writerow(data)
    print(f"Data written to {csv_file_path}")

def process_worksheet_dependencies(root, ws_csv_file_path):
    with open(ws_csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Worksheet Name', 'Datasource', 'Column Caption', 'Column Name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for worksheet in root.findall('.//worksheet'):
            worksheet_name = worksheet.attrib.get('name', '')
            datasources_dict = {}
            for ds in worksheet.findall('.//view/datasources/datasource'):
                caption = ds.attrib.get('caption', '')
                name = ds.attrib.get('name', '')
                if name:
                    datasources_dict[name] = caption if caption else name
            for ds_dep in worksheet.findall('.//view/datasource-dependencies'):
                ds_name = ds_dep.attrib.get('datasource', '')
                ds_detail = datasources_dict.get(ds_name, ds_name)
                for column in ds_dep.findall('column'):
                    column_caption = column.attrib.get('caption', '')
                    column_name = column.attrib.get('name', '')
                    if not column_caption:
                        column_caption = column_name
                    writer.writerow({
                        'Worksheet Name': worksheet_name,
                        'Datasource': ds_detail,
                        'Column Caption': column_caption,
                        'Column Name': column_name
                    })
    print(f"Data written to {ws_csv_file_path}")

def process_workbook_structure(root, ds_csv_file_path):
    seen_combinations = set()
    with open(ds_csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Worksheet Name', 'Dashboard Name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for dashboard in root.findall(".//dashboard"):
            dashboard_name = dashboard.get('name')
            for worksheet in dashboard.findall(".//zone[@name]"):
                worksheet_name = worksheet.get('name')
                combo = (worksheet_name, dashboard_name)
                if combo not in seen_combinations:
                    writer.writerow({'Worksheet Name': worksheet_name, 'Dashboard Name': dashboard_name})
                    seen_combinations.add(combo)
    print("CSV file for workbook structure has been created!")

def merge_and_sort_csvs(ws_csv_file_path, ds_csv_file_path, output_csv_file_path):
    df1 = pd.read_csv(ws_csv_file_path, encoding=UTF8)
    df2 = pd.read_csv(ds_csv_file_path, encoding=UTF8)
    merged_df = pd.merge(df1, df2, on="Worksheet Name")
    column_order = ["Dashboard Name", "Worksheet Name", "Datasource", "Column Caption", "Column Name"]
    sorted_df = merged_df[column_order].sort_values(by=column_order)
    sorted_df.to_csv(output_csv_file_path, index=False)
    print(f"Merged, rearranged, and sorted CSV file has been created: {output_csv_file_path}")

def main():
    xml_file_path = f"{BASE_DEST_DIR}/<NAME OF TWB FILE>.twb"  # Define the path to the .twb file
    csv_file_path = f"{BASE_DEST_DIR}/output_calculated_fields.csv"
    ws_csv_file_path = f"{BASE_DEST_DIR}/output_worksheet_dependencies.csv"
    ds_csv_file_path = f"{BASE_DEST_DIR}/output_workbook_structure.csv"
    output_csv_file_path = f"{BASE_DEST_DIR}/merged_output.csv"

    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    process_calculated_fields(root, csv_file_path)
    process_worksheet_dependencies(root, ws_csv_file_path)
    process_workbook_structure(root, ds_csv_file_path)
    merge_and_sort_csvs(ws_csv_file_path, ds_csv_file_path, output_csv_file_path)

if __name__ == "__main__":
    main()
