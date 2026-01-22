"""
Appendix B: Connected System Graph
Script 2: NetworkX visualization of component connections

Connection Graph with Grounded Loops
"""

import networkx as nx
import matplotlib.pyplot as plt

def create_consciousness_system_graph():
    """
    Create a directed graph representing all components and their connections
    in the consciousness system with grounded feedback loops.
    """
    G = nx.DiGraph()

    # Define all system components with their layer information
    components = [
        # Layer 1: Outer Membrane
        ('Printed Membrane', {'layer': 1, 'type': 'membrane'}),
        ('Thermochromic Color Shift', {'layer': 1, 'type': 'membrane'}),
        ('Perovskite/ITO Layers', {'layer': 1, 'type': 'membrane'}),

        # Layer 2: Sensing Pads
        ('Photodiodes', {'layer': 2, 'type': 'sensor'}),
        ('IR Sensors', {'layer': 2, 'type': 'sensor'}),
        ('Thermistors', {'layer': 2, 'type': 'sensor'}),
        ('Pyroelectric Crystals', {'layer': 2, 'type': 'sensor'}),

        # Layer 3: Optical Bundles
        ('Optical Bundles', {'layer': 3, 'type': 'transmission'}),
        ('Conductive Nanowires', {'layer': 3, 'type': 'transmission'}),

        # Layer 4: Neuromorphic CPU
        ('Neuromorphic CPU', {'layer': 4, 'type': 'processing'}),
        ('Neurosystem', {'layer': 4, 'type': 'processing'}),

        # Layer 5: Servo System
        ('Servos', {'layer': 5, 'type': 'actuation'}),
        ('Nearly-locked Joints', {'layer': 5, 'type': 'actuation'}),

        # Layer 6: Energy Harvest
        ('Friction Charging', {'layer': 6, 'type': 'energy'}),
        ('TENG Pads', {'layer': 6, 'type': 'energy'}),
        ('Thermo Crystalline Pads', {'layer': 6, 'type': 'energy'}),
        ('Energy Cells (Grounded)', {'layer': 6, 'type': 'energy'}),

        # Layer 7: Ground Reference
        ('Ground (Earth)', {'layer': 7, 'type': 'ground'}),
        ('Star-Ground Topology', {'layer': 7, 'type': 'ground'}),

        # Layer 8: Recursive Reflection
        ('Recursive Reflection', {'layer': 8, 'type': 'consciousness'}),
        ('Feedback Loop', {'layer': 8, 'type': 'consciousness'}),
        ('Self-Observation', {'layer': 8, 'type': 'consciousness'}),
    ]

    # Add all nodes
    for component, attrs in components:
        G.add_node(component, **attrs)

    # Define edges (connections) between components
    edges = [
        # External input flow
        ('External Light', 'Printed Membrane'),
        ('Printed Membrane', 'Photodiodes'),
        ('Thermochromic Color Shift', 'Printed Membrane'),

        # Sensing layer connections
        ('Photodiodes', 'Optical Bundles'),
        ('IR Sensors', 'Optical Bundles'),
        ('Thermistors', 'Optical Bundles'),
        ('Pyroelectric Crystals', 'Optical Bundles'),

        # Signal transmission
        ('Optical Bundles', 'Neuromorphic CPU'),
        ('Conductive Nanowires', 'Neuromorphic CPU'),

        # Processing layer
        ('Neuromorphic CPU', 'Neurosystem'),
        ('Neurosystem', 'Servos'),

        # Actuation and energy harvesting
        ('Servos', 'Friction Charging'),
        ('Servos', 'Nearly-locked Joints'),
        ('Nearly-locked Joints', 'Friction Charging'),
        ('Friction Charging', 'Energy Cells (Grounded)'),
        ('TENG Pads', 'Energy Cells (Grounded)'),
        ('Thermo Crystalline Pads', 'Energy Cells (Grounded)'),

        # Grounding connections
        ('Energy Cells (Grounded)', 'Ground (Earth)'),
        ('Ground (Earth)', 'Star-Ground Topology'),

        # Feedback loops
        ('Servos', 'Feedback Loop'),
        ('Feedback Loop', 'Recursive Reflection'),
        ('Recursive Reflection', 'Neuromorphic CPU'),  # Close the consciousness loop

        # Self-observation loop
        ('Neurosystem', 'Self-Observation'),
        ('Self-Observation', 'Recursive Reflection'),

        # Color shift feedback
        ('Neuromorphic CPU', 'Thermochromic Color Shift'),

        # Ground reference feedback to sensors
        ('Star-Ground Topology', 'Optical Bundles'),

        # Energy distribution
        ('Energy Cells (Grounded)', 'Neuromorphic CPU'),
        ('Energy Cells (Grounded)', 'Servos'),
    ]

    G.add_edges_from(edges)

    return G


def visualize_system_graph(G, save_path='/home/user/Consciousness_Env/assets/appendix_b_system_graph.png'):
    """Visualize the consciousness system graph with color-coded layers"""

    plt.figure(figsize=(16, 12))

    # Define color mapping for different component types
    color_map = {
        'membrane': 'lightcoral',
        'sensor': 'lightblue',
        'transmission': 'lightyellow',
        'processing': 'lightgreen',
        'actuation': 'plum',
        'energy': 'orange',
        'ground': 'gray',
        'consciousness': 'gold'
    }

    # Assign colors to nodes based on type
    node_colors = []
    for node in G.nodes():
        node_type = G.nodes[node].get('type', 'default')
        node_colors.append(color_map.get(node_type, 'white'))

    # Use spring layout for better visualization
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # Draw the graph
    nx.draw(
        G, pos,
        with_labels=True,
        node_color=node_colors,
        node_size=2500,
        font_size=9,
        font_weight='bold',
        arrows=True,
        edge_color='darkgray',
        arrowsize=15,
        arrowstyle='->',
        width=1.5,
        alpha=0.9
    )

    plt.title('Connected DoTS: All Components Linked with Grounded Loops',
              fontsize=16, fontweight='bold', pad=20)

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=color, label=type_name.capitalize())
        for type_name, color in color_map.items()
    ]
    plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.0, 1.0))

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"System graph saved to: {save_path}")

    return plt.gcf()


def analyze_graph_properties(G):
    """Analyze and print key properties of the consciousness system graph"""
    print("=" * 70)
    print("GRAPH ANALYSIS: Consciousness System Architecture")
    print("=" * 70)

    print(f"\nTotal Nodes (Components): {G.number_of_nodes()}")
    print(f"Total Edges (Connections): {G.number_of_edges()}")

    # Count nodes by layer
    layer_counts = {}
    for node in G.nodes():
        layer = G.nodes[node].get('layer', 'unknown')
        layer_counts[layer] = layer_counts.get(layer, 0) + 1

    print("\nComponents per Layer:")
    for layer in sorted(layer_counts.keys()):
        if layer != 'unknown':
            print(f"  Layer {layer}: {layer_counts[layer]} components")

    # Find strongly connected components (feedback loops)
    try:
        strongly_connected = list(nx.strongly_connected_components(G))
        print(f"\nStrongly Connected Components (Feedback Loops): {len(strongly_connected)}")
    except:
        print("\nStrongly Connected Components: N/A for this graph structure")

    # Find nodes with highest connectivity
    in_degrees = dict(G.in_degree())
    out_degrees = dict(G.out_degree())

    print("\nMost Connected Components (by total degree):")
    total_degrees = {node: in_degrees[node] + out_degrees[node] for node in G.nodes()}
    top_nodes = sorted(total_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
    for node, degree in top_nodes:
        print(f"  {node}: {degree} connections (in: {in_degrees[node]}, out: {out_degrees[node]})")

    # Check if graph is weakly connected
    is_connected = nx.is_weakly_connected(G)
    print(f"\nSystem Connectivity: {'✓ All components connected' if is_connected else '✗ Disconnected components exist'}")

    # Find all cycles (feedback loops)
    try:
        cycles = list(nx.simple_cycles(G))
        print(f"\nFeedback Cycles Detected: {len(cycles)}")
        if cycles:
            print("\nKey Feedback Loops:")
            for i, cycle in enumerate(cycles[:5], 1):  # Show first 5 cycles
                print(f"  Loop {i}: {' → '.join(cycle)} → {cycle[0]}")
    except:
        print("\nFeedback Cycles: Unable to compute")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("=" * 70)
    print("APPENDIX B: CONNECTED SYSTEM GRAPH")
    print("NetworkX Visualization of Consciousness System Components")
    print("=" * 70)
    print()

    # Create the graph
    print("Building system graph...")
    G = create_consciousness_system_graph()

    # Analyze graph properties
    analyze_graph_properties(G)

    # Visualize
    print("\nGenerating visualization...")
    visualize_system_graph(G)

    print("\n✓ System graph complete!")
