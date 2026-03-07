---
name: patent-diagram-generator
description: Create patent-style technical diagrams including flowcharts, block diagrams, and system architectures using Graphviz with reference numbering
tools: Bash, Read, Write
model: sonnet
---

# Patent Diagram Generator Skill

Create patent-style technical diagrams including flowcharts, block diagrams, and system architectures using Graphviz.

## When to Use

Invoke this skill when users ask to:
- Create flowcharts for method claims
- Generate block diagrams for system claims
- Draw system architecture diagrams
- Create technical illustrations for patents
- Add reference numbers to diagrams
- Generate patent figures

## What This Skill Does

1. **Flowchart Generation**:
   - Method step flowcharts
   - Decision trees
   - Process flows with branches
   - Patent-style step numbering

2. **Block Diagram Creation**:
   - System component diagrams
   - Hardware architecture diagrams
   - Software module diagrams
   - Component interconnections

3. **Custom Diagram Rendering**:
   - Render Graphviz DOT code
   - Support multiple formats (SVG, PNG, PDF)
   - Multiple layout engines (dot, neato, fdp, circo, twopi)

4. **Patent-Style Formatting**:
   - Add reference numbers (10, 20, 30, etc.)
   - Use clear labels and connections
   - Professional formatting for USPTO filing

## Required Dependencies

This skill requires Graphviz to be installed:

**Linux**:
```bash
sudo apt install graphviz
```

**Python Package**:
```bash
pip install graphviz
```

## How to Use

When this skill is invoked:

1. **Create flowchart** from steps:
   ```python
   import graphviz

   dot = graphviz.Digraph(comment='Patent Method Flowchart')
   dot.attr(rankdir='TB')
   dot.node('start', 'Start', shape='ellipse')
   dot.node('step1', 'Initialize System', shape='box')
   dot.node('decision', 'Is Valid?', shape='diamond')
   dot.node('step2', 'Process Data', shape='box')
   dot.node('error', 'Handle Error', shape='box')
   dot.node('end', 'End', shape='ellipse')
   dot.edge('start', 'step1')
   dot.edge('step1', 'decision')
   dot.edge('decision', 'step2', label='Yes')
   dot.edge('decision', 'error', label='No')
   dot.edge('step2', 'end')
   dot.edge('error', 'end')
   dot.render('method_flowchart', format='svg', cleanup=True)
   ```

2. **Render custom DOT code**:
   ```python
   dot_code = """
   digraph PatentSystem {
       rankdir=LR;
       node [shape=box, style=rounded];
       Input [label="User Input\n(10)"];
       Processor [label="Processing Unit\n(20)"];
       Output [label="Display\n(30)"];
       Input -> Processor [label="data"];
       Processor -> Output [label="result"];
   }
   """
   src = graphviz.Source(dot_code)
   src.render('custom_diagram', format='svg', cleanup=True)
   ```

## Patent-Style Reference Numbers

Convention:
- Main components: 10, 20, 30, 40, ...
- Sub-components: 12, 14, 16 (under 10)
- Elements: 22, 24, 26 (under 20)

## Shape Types

### Flowchart Shapes
- `ellipse`: Start/End points
- `box`: Process steps
- `diamond`: Decision points
- `parallelogram`: Input/Output operations
- `cylinder`: Database/Storage

### Block Diagram Types
- `input`: Input devices/sensors
- `output`: Output devices/displays
- `process`: Processing units
- `storage`: Memory/storage
- `decision`: Control logic

## Layout Engines

- `dot`: Hierarchical (top-down/left-right)
- `neato`: Spring model layout
- `fdp`: Force-directed layout
- `circo`: Circular layout
- `twopi`: Radial layout

## Output Formats

- `svg`: Scalable Vector Graphics (best for editing)
- `png`: Raster image (good for viewing)
- `pdf`: Portable Document Format (USPTO compatible)
