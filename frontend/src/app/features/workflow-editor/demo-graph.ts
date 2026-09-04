import type { WorkflowGraph } from './graph.model';

const TEXT_INPUT_ID = '11111111-1111-1111-1111-111111111111';
const PROMPT_ID = '22222222-2222-2222-2222-222222222222';
const OUTPUT_ID = '33333333-3333-3333-3333-333333333333';

export const DEMO_GRAPH: WorkflowGraph = {
  nodes: [
    { id: TEXT_INPUT_ID, type: 'text_input', position: { x: 80, y: 120 }, config: {} },
    { id: PROMPT_ID, type: 'prompt', position: { x: 420, y: 120 }, config: {} },
    { id: OUTPUT_ID, type: 'output', position: { x: 760, y: 120 }, config: {} },
  ],
  edges: [
    {
      id: '44444444-4444-4444-4444-444444444444',
      fromNode: TEXT_INPUT_ID,
      fromPort: 'text',
      toNode: PROMPT_ID,
      toPort: 'context',
    },
    {
      id: '55555555-5555-5555-5555-555555555555',
      fromNode: PROMPT_ID,
      fromPort: 'result',
      toNode: OUTPUT_ID,
      toPort: 'value',
    },
  ],
};
