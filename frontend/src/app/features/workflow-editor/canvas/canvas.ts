import {
  type AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  Injector,
  type OnDestroy,
  ViewChild,
  inject,
} from '@angular/core';
import { DEMO_GRAPH } from '../demo-graph';
import { NodeTypesStore } from '../state/node-types-store';
import { WorkflowStore } from '../state/workflow-store';
import { createWorkflowCanvas, type WorkflowCanvas } from './editor-factory';

const WORKFLOW_NAME = 'My Workflow';

@Component({
  selector: 'app-workflow-canvas',
  templateUrl: './canvas.html',
  styleUrl: './canvas.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Canvas implements AfterViewInit, OnDestroy {
  @ViewChild('container') private readonly containerRef!: ElementRef<HTMLDivElement>;

  private readonly injector = inject(Injector);
  private readonly nodeTypesStore = inject(NodeTypesStore);
  protected readonly store = inject(WorkflowStore);

  private canvas: WorkflowCanvas | null = null;

  async ngAfterViewInit(): Promise<void> {
    const [nodeTypes] = await Promise.all([
      this.nodeTypesStore.load(),
      this.store.openByName(WORKFLOW_NAME),
    ]);

    this.canvas = await createWorkflowCanvas(
      this.containerRef.nativeElement,
      this.injector,
      nodeTypes,
    );
    const graph = this.store.graph();
    await this.canvas.loadGraph(graph.nodes.length > 0 ? graph : DEMO_GRAPH);
  }

  ngOnDestroy(): void {
    this.canvas?.destroy();
  }

  async onSave(): Promise<void> {
    if (!this.canvas) {
      return;
    }
    await this.store.save(this.canvas.exportGraph());
  }
}
