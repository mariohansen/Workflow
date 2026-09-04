import { Injectable, computed, inject, signal } from '@angular/core';
import { WorkflowsApiService } from '../../../api/workflows-api.service';
import type { WorkflowGraph } from '../graph.model';
import { fromApiGraph, toApiGraph } from './graph-mapper';

@Injectable({ providedIn: 'root' })
export class WorkflowStore {
  private readonly api = inject(WorkflowsApiService);

  private readonly _workflowId = signal<string | null>(null);
  private readonly _graph = signal<WorkflowGraph>({ nodes: [], edges: [] });
  private readonly _version = signal<number | null>(null);
  private readonly _saving = signal(false);

  readonly workflowId = this._workflowId.asReadonly();
  readonly graph = this._graph.asReadonly();
  readonly version = this._version.asReadonly();
  readonly saving = this._saving.asReadonly();
  readonly hasWorkflow = computed(() => this._workflowId() !== null);

  async openByName(name: string): Promise<void> {
    const existing = (await this.api.listWorkflows()).find((workflow) => workflow.name === name);
    const workflow = existing ?? (await this.api.createWorkflow(name));

    const latest = await this.api.getLatestVersion(workflow.id);
    this._workflowId.set(workflow.id);
    this._version.set(latest?.version ?? null);
    this._graph.set(latest ? fromApiGraph(latest.graph) : { nodes: [], edges: [] });
  }

  async save(graph: WorkflowGraph): Promise<void> {
    const workflowId = this._workflowId();
    if (workflowId === null) {
      throw new Error('cannot save: no workflow open');
    }

    this._saving.set(true);
    try {
      const saved = await this.api.saveVersion(workflowId, toApiGraph(graph));
      this._graph.set(fromApiGraph(saved.graph));
      this._version.set(saved.version);
    } finally {
      this._saving.set(false);
    }
  }
}
