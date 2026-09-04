import { ClassicPreset as Classic, type GetSchemes } from 'rete';

export class ReteNode extends Classic.Node {
  width = 180;
  height = 140;

  constructor(
    public readonly workflowType: string,
    label: string,
  ) {
    super(label);
  }
}

export const anySocket = new Classic.Socket('any');

export class ReteConnection<
  Source extends ReteNode = ReteNode,
  Target extends ReteNode = ReteNode,
> extends Classic.Connection<Source, Target> {}

export type Schemes = GetSchemes<ReteNode, ReteConnection>;
