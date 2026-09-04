import type { Injector } from '@angular/core';
import { NodeEditor } from 'rete';
import { type AngularArea2D, AngularPlugin, Presets as AngularPresets } from 'rete-angular-plugin/22';
import { type Area2D, AreaExtensions, AreaPlugin } from 'rete-area-plugin';
import { ConnectionPlugin, Presets as ConnectionPresets } from 'rete-connection-plugin';
import type { WorkflowGraph } from '../graph.model';
import { exportGraph, loadGraph } from './graph-adapter';
import type { Schemes } from './schemes';

type AreaExtra = Area2D<Schemes> | AngularArea2D<Schemes>;

export interface WorkflowCanvas {
  loadGraph(graph: WorkflowGraph): Promise<void>;
  exportGraph(): WorkflowGraph;
  destroy(): void;
}

export async function createWorkflowCanvas(
  container: HTMLElement,
  injector: Injector,
): Promise<WorkflowCanvas> {
  const editor = new NodeEditor<Schemes>();
  const area = new AreaPlugin<Schemes, AreaExtra>(container);
  const connection = new ConnectionPlugin<Schemes, AreaExtra>();
  const render = new AngularPlugin<Schemes, AreaExtra>({ injector });

  render.addPreset(AngularPresets.classic.setup());
  connection.addPreset(ConnectionPresets.classic.setup());

  editor.use(area);
  area.use(render);
  area.use(connection);

  const selector = AreaExtensions.selector();
  const accumulating = AreaExtensions.accumulateOnCtrl();
  AreaExtensions.selectableNodes(area, selector, { accumulating });
  AreaExtensions.simpleNodesOrder(area);

  return {
    async loadGraph(graph) {
      await loadGraph(editor, area, graph);
      await AreaExtensions.zoomAt(area, editor.getNodes());
    },
    exportGraph() {
      return exportGraph(editor, area);
    },
    destroy() {
      area.destroy();
    },
  };
}
