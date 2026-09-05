import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { API_BASE_URL } from './workflows-api.service';
import type { components } from './schema';

export type NodeTypeDto = components['schemas']['NodeTypeDto'];

@Injectable({ providedIn: 'root' })
export class NodeTypesApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = inject(API_BASE_URL);

  listNodeTypes(): Promise<NodeTypeDto[]> {
    return firstValueFrom(this.http.get<NodeTypeDto[]>(`${this.baseUrl}/node-types`));
  }
}
