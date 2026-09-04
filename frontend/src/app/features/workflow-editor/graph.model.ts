export interface Position {
  x: number;
  y: number;
}

export interface PortDescriptor {
  name: string;
  label: string;
}

export interface WorkflowNode {
  id: string;
  type: string;
  label: string;
  position: Position;
  inputs: PortDescriptor[];
  outputs: PortDescriptor[];
}

export interface WorkflowEdge {
  id: string;
  fromNode: string;
  fromPort: string;
  toNode: string;
  toPort: string;
}

export interface WorkflowGraph {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}
