import { Injectable, inject, signal } from '@angular/core';
import { NodeTypesApiService } from '../../../api/node-types-api.service';
import type { NodeTypeDescriptor } from '../node-types';
import { fromApiNodeType } from './node-types-mapper';

@Injectable({ providedIn: 'root' })
export class NodeTypesStore {
  private readonly api = inject(NodeTypesApiService);

  private readonly _byType = signal<Record<string, NodeTypeDescriptor>>({});
  readonly byType = this._byType.asReadonly();

  async load(): Promise<Record<string, NodeTypeDescriptor>> {
    const dtos = await this.api.listNodeTypes();
    const byType = Object.fromEntries(dtos.map((dto) => [dto.type, fromApiNodeType(dto)]));
    this._byType.set(byType);
    return byType;
  }
}
