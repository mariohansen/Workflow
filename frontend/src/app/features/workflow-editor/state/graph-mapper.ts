import type { GraphDto } from '../../../api/workflows-api.service';
import type { WorkflowGraph } from '../graph.model';

export function toApiGraph(graph: WorkflowGraph): GraphDto {
  return {
    nodes: graph.nodes.map((node) => ({
      id: node.id,
      type: node.type,
      position: node.position,
      config: node.config,
    })),
    edges: graph.edges.map((edge) => ({
      id: edge.id,
      from_node: edge.fromNode,
      from_port: edge.fromPort,
      to_node: edge.toNode,
      to_port: edge.toPort,
    })),
  };
}

export function fromApiGraph(graph: GraphDto): WorkflowGraph {
  return {
    nodes: graph.nodes.map((node) => ({
      id: node.id,
      type: node.type,
      position: node.position,
      config: node.config as Record<string, unknown>,
    })),
    edges: graph.edges.map((edge) => ({
      id: edge.id,
      fromNode: edge.from_node,
      fromPort: edge.from_port,
      toNode: edge.to_node,
      toPort: edge.to_port,
    })),
  };
}
