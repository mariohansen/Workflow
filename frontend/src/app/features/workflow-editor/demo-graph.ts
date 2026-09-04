import type { WorkflowGraph } from './graph.model';

export const DEMO_GRAPH: WorkflowGraph = {
  nodes: [
    {
      id: 'demo-text-input',
      type: 'text_input',
      label: 'Text Input',
      position: { x: 80, y: 120 },
      inputs: [],
      outputs: [{ name: 'text', label: 'Text' }],
    },
    {
      id: 'demo-prompt',
      type: 'prompt',
      label: 'Prompt',
      position: { x: 420, y: 120 },
      inputs: [{ name: 'context', label: 'Context' }],
      outputs: [{ name: 'result', label: 'Result' }],
    },
    {
      id: 'demo-output',
      type: 'output',
      label: 'Output',
      position: { x: 760, y: 120 },
      inputs: [{ name: 'value', label: 'Value' }],
      outputs: [],
    },
  ],
  edges: [
    {
      id: 'demo-edge-1',
      fromNode: 'demo-text-input',
      fromPort: 'text',
      toNode: 'demo-prompt',
      toPort: 'context',
    },
    {
      id: 'demo-edge-2',
      fromNode: 'demo-prompt',
      fromPort: 'result',
      toNode: 'demo-output',
      toPort: 'value',
    },
  ],
};
