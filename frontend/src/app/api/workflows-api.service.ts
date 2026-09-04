import { HttpClient } from '@angular/common/http';
import { InjectionToken, Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import type { components } from './schema';

export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL', {
  providedIn: 'root',
  factory: () => 'http://localhost:8000',
});

export type WorkflowDto = components['schemas']['WorkflowResponse'];
export type WorkflowVersionDto = components['schemas']['WorkflowVersionResponse'];
export type GraphDto = components['schemas']['GraphDto'];

@Injectable({ providedIn: 'root' })
export class WorkflowsApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = inject(API_BASE_URL);

  createWorkflow(name: string): Promise<WorkflowDto> {
    return firstValueFrom(
      this.http.post<WorkflowDto>(`${this.baseUrl}/workflows`, { name }),
    );
  }

  listWorkflows(): Promise<WorkflowDto[]> {
    return firstValueFrom(this.http.get<WorkflowDto[]>(`${this.baseUrl}/workflows`));
  }

  getLatestVersion(workflowId: string): Promise<WorkflowVersionDto | null> {
    return firstValueFrom(
      this.http.get<WorkflowVersionDto | null>(
        `${this.baseUrl}/workflows/${workflowId}/versions/latest`,
      ),
    );
  }

  saveVersion(workflowId: string, graph: GraphDto): Promise<WorkflowVersionDto> {
    return firstValueFrom(
      this.http.post<WorkflowVersionDto>(
        `${this.baseUrl}/workflows/${workflowId}/versions`,
        graph,
      ),
    );
  }
}
