import type { NodeTypeDto } from '../../../api/node-types-api.service';
import type { NodeTypeDescriptor } from '../node-types';

export function fromApiNodeType(dto: NodeTypeDto): NodeTypeDescriptor {
  return {
    type: dto.type,
    label: dto.label,
    inputs: dto.inputs.map((port) => ({ name: port.name, label: port.label })),
    outputs: dto.outputs.map((port) => ({ name: port.name, label: port.label })),
  };
}
