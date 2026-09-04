export interface PortDescriptor {
  name: string;
  label: string;
}

export interface NodeTypeDescriptor {
  type: string;
  label: string;
  inputs: PortDescriptor[];
  outputs: PortDescriptor[];
}

/**
 * Stand-in for the backend step registry (`GET /node-types`, section 7 of
 * CLAUDE.md), which doesn't exist until the engine is built. Lists exactly
 * the MVP step types so the canvas has something to render ports from.
 */
export const NODE_TYPES: Record<string, NodeTypeDescriptor> = {
  text_input: {
    type: 'text_input',
    label: 'Text Input',
    inputs: [],
    outputs: [{ name: 'text', label: 'Text' }],
  },
  document_input: {
    type: 'document_input',
    label: 'Document Input',
    inputs: [],
    outputs: [{ name: 'document', label: 'Document' }],
  },
  context: {
    type: 'context',
    label: 'Context',
    inputs: [],
    outputs: [{ name: 'context', label: 'Context' }],
  },
  prompt: {
    type: 'prompt',
    label: 'Prompt',
    inputs: [{ name: 'context', label: 'Context' }],
    outputs: [{ name: 'result', label: 'Result' }],
  },
  manual_llm: {
    type: 'manual_llm',
    label: 'Manual LLM',
    inputs: [{ name: 'prompt', label: 'Prompt' }],
    outputs: [{ name: 'response', label: 'Response' }],
  },
  output: {
    type: 'output',
    label: 'Output',
    inputs: [{ name: 'value', label: 'Value' }],
    outputs: [],
  },
};
