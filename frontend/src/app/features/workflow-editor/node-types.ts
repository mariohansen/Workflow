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
