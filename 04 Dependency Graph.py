# =====================================
# Combined Imports
# =====================================
import csv
import re
import networkx as nx
from pyvis.network import Network
import json
import matplotlib.colors as mcolors
import matplotlib.cm as cm

# =====================================
# Combined Configuration
# =====================================
BASE_DEST_DIR = r"<PATH TO WORKING DIRECTORY>"
BASE_FILE = "output_calculated_fields.csv"
FILE_INPUT = f"{BASE_DEST_DIR}/{BASE_FILE}"
FILE_OUTPUT = f"{BASE_DEST_DIR}/edges.csv"
OUTPUT_HTML = "network_visualization.html"

# =====================================
# Functions from Script 1
# =====================================
def load_data(filepath: str) -> list:
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

def extract_caption_mapping(data: list) -> dict:
    return {row['Name']: (row['Caption'] if row['Caption'] else row['Name']) for row in data}

def parse_formula_for_references(formula: str) -> list:
    references = re.findall(r'\[[^\]]*\]', formula)
    return [ref.replace("[Parameters].", "").strip() for ref in references if ref != "[Parameters]"]

def extract_edges(data: list, name_to_caption: dict) -> set:
    edges_set = set()
    for row in data:
        formula = row['Calculation Formula']
        name = row['Name']
        if formula:
            references = re.findall(r'\[[^\]]*\]', formula)
            references = [ref.replace("[Parameters].", "") for ref in references if ref != "[Parameters]"]
            for ref_name in references:
                source = name_to_caption.get(name, name)
                target = name_to_caption.get(ref_name, ref_name)
                edges_set.add((source, target))
    return edges_set

def save_edges_to_csv(edges: list, filepath: str):
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Source', 'Target'])
        writer.writerows(edges)

# =====================================
# Functions from Script 2
# =====================================
def load_data_from_csv(file_path: str) -> nx.DiGraph():
    G = nx.DiGraph()
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            edges = [tuple(row) for row in reader]
            G.add_edges_from(edges)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    return G

def compute_node_attributes(G: nx.DiGraph, nt: Network):
    degrees = dict(G.degree())
    max_degree = max(degrees.values())
    normalized_degrees = {node: degree / max_degree for node, degree in degrees.items()}
    in_degrees = dict(G.in_degree())
    out_degrees = dict(G.out_degree())
    color_map = cm.get_cmap('Blues')
    for node in nt.nodes:
        node_id = node['id']
        normalized_degree = normalized_degrees[node_id]
        rgba_color = color_map(normalized_degree)
        hex_color = mcolors.to_hex(rgba_color)
        node.update({
            'title': f"Field name: [{node['label']}]\n{in_degrees[node_id]} fields are based on this one.\nThis field uses {out_degrees[node_id]} other fields.",
            'color': hex_color,
            'size': 10,
            'font': {'size': 8}
        })

def compute_edge_attributes(nt: Network):
    for edge in nt.edges:
        source = edge['from']
        target = edge['to']
        edge.update({
            'color': 'gray',
            'arrows': {'from': {'enabled': True, 'type': 'arrow'}},
            'scaling': {'factor': 1},
            'smooth': {'type': 'dynamic', 'roundness': 1},
            'title': f"From [{source}] to [{target}]"
        })

# =====================================
# Merged Main Execution
# =====================================
if __name__ == "__main__":
    # From Script 1
    try:
        data = load_data(FILE_INPUT)
        name_to_caption = extract_caption_mapping(data)
        edges = extract_edges(data, name_to_caption)
        save_edges_to_csv(edges, FILE_OUTPUT)
    except Exception as e:
        print(f"An error occurred: {e}")

    # From Script 2
    G_nx = load_data_from_csv(FILE_OUTPUT)
    nt = Network(notebook=True)
    nt.from_nx(G_nx)
    compute_node_attributes(G_nx, nt)
    compute_edge_attributes(nt)
    nt.toggle_physics(True)
    physics_options = {
        "solver": "barnesHut",
        "barnesHut": {
            "gravitationalConstant": -3000,
            "centralGravity": 0.5,
            "springLength": 95,
            "springConstant": 0.04,
            "damping": 0.09,
            "avoidOverlap": 0.1
        },
        "minVelocity": 0.75,
        "timestep": 0.5
    }
    options_str = json.dumps({"physics": physics_options})
    nt.set_options(options_str)
    nt.show(f"{BASE_DEST_DIR}/{OUTPUT_HTML}")
