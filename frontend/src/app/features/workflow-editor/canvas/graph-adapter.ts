import { ClassicPreset as Classic, type NodeEditor } from 'rete';
import type { AreaPlugin } from 'rete-area-plugin';
import type { WorkflowEdge, WorkflowGraph, WorkflowNode } from '../graph.model';
import type { NodeTypeDescriptor } from '../node-types';
import { anySocket, ReteConnection, ReteNode, type Schemes } from './schemes';

function buildReteNode(node: WorkflowNode, nodeTypes: Readonly<Record<string, NodeTypeDescriptor>>): ReteNode {
  const descriptor = nodeTypes[node.type];
  if (!descriptor) {
    throw new Error(`unknown node type: ${node.type}`);
  }

  const reteNode = new ReteNode(node.type, descriptor.label, node.config);
  reteNode.id = node.id;

  for (const input of descriptor.inputs) {
    reteNode.addInput(input.name, new Classic.Input(anySocket, input.label));
  }
  for (const output of descriptor.outputs) {
    reteNode.addOutput(output.name, new Classic.Output(anySocket, output.label));
  }

  return reteNode;
}

function buildReteConnection(edge: WorkflowEdge, nodes: ReadonlyMap<string, ReteNode>): ReteConnection {
  const source = nodes.get(edge.fromNode);
  const target = nodes.get(edge.toNode);
  if (!source || !target) {
    throw new Error(`edge ${edge.id} references a node that does not exist`);
  }

  const connection = new ReteConnection(source, edge.fromPort, target, edge.toPort);
  connection.id = edge.id;
  return connection;
}

export async function loadGraph<AreaExtra>(
  editor: NodeEditor<Schemes>,
  area: AreaPlugin<Schemes, AreaExtra>,
  graph: WorkflowGraph,
  nodeTypes: Readonly<Record<string, NodeTypeDescriptor>>,
): Promise<void> {
  const nodes = new Map<string, ReteNode>();

  for (const node of graph.nodes) {
    const reteNode = buildReteNode(node, nodeTypes);
    nodes.set(node.id, reteNode);
    await editor.addNode(reteNode);
    await area.translate(reteNode.id, node.position);
  }

  for (const edge of graph.edges) {
    await editor.addConnection(buildReteConnection(edge, nodes));
  }
}

export function exportGraph<AreaExtra>(
  editor: NodeEditor<Schemes>,
  area: AreaPlugin<Schemes, AreaExtra>,
): WorkflowGraph {
  const nodes: WorkflowNode[] = editor.getNodes().map((node) => ({
    id: node.id,
    type: node.workflowType,
    position: area.nodeViews.get(node.id)?.position ?? { x: 0, y: 0 },
    config: node.config,
  }));

  const edges: WorkflowEdge[] = editor.getConnections().map((connection) => ({
    id: connection.id,
    fromNode: connection.source,
    fromPort: String(connection.sourceOutput),
    toNode: connection.target,
    toPort: String(connection.targetInput),
  }));

  return { nodes, edges };
}
