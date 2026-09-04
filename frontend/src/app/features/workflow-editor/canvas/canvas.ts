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
import { createWorkflowCanvas, type WorkflowCanvas } from './editor-factory';

@Component({
  selector: 'app-workflow-canvas',
  templateUrl: './canvas.html',
  styleUrl: './canvas.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Canvas implements AfterViewInit, OnDestroy {
  @ViewChild('container') private readonly containerRef!: ElementRef<HTMLDivElement>;

  private readonly injector = inject(Injector);
  private canvas: WorkflowCanvas | null = null;

  async ngAfterViewInit(): Promise<void> {
    this.canvas = await createWorkflowCanvas(this.containerRef.nativeElement, this.injector);
    await this.canvas.loadGraph(DEMO_GRAPH);
  }

  ngOnDestroy(): void {
    this.canvas?.destroy();
  }
}
