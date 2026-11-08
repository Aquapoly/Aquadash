import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject } from 'rxjs';

import { SERVER_URL } from '@app/environment';
import { TimelapseConfig, TimelapseMetadata, TimelapseStatus } from '@app/interfaces/timelapse';
import { TimelapseStatusDto } from '@app/interfaces/timelapse.dto';
import { mapTimelapseStatusDto } from '@app/interfaces/timelapse.mapper';
import { TimelapseStoreService } from '@app/services/timelapse-store.service';
import { TimelapseWebSocketService } from '@app/services/timelapse-websocket.service';

@Injectable({ providedIn: 'root' })
export class TimelapseSessionService {
  private readonly _status$ = new BehaviorSubject<TimelapseStatus | null>(null);
  readonly status$ = this._status$.asObservable();

  private readonly _error$ = new BehaviorSubject<string | null>(null);
  readonly error$ = this._error$.asObservable();

  get statusSnapshot(): TimelapseStatus | null {
    return this._status$.value;
  }

  constructor(
    private readonly http: HttpClient,
    private readonly store: TimelapseStoreService,
    webSocketService: TimelapseWebSocketService,
  ) {
    webSocketService.status$.subscribe(status => this.updateStatus(status));
    this.refreshStatus();
  }

  refreshStatus(): void {
    this.http.get<TimelapseStatusDto>(`${SERVER_URL}/timelapse/status`).subscribe({
      next: status => this.updateStatus(status),
      error: err => {
        this._error$.next(
          `Échec de l'obtention du statut du timelapse: ${err.error?.detail || err.message}`,
        );
      },
    });
  }

  start(config: TimelapseConfig): void {
    this._error$.next(null);
    this.http.post<TimelapseStatusDto>(`${SERVER_URL}/timelapse/start`, config).subscribe({
      next: status => this.updateStatus(status),
      error: err => {
        this._error$.next(
          `Échec du démarrage du timelapse: ${err.error?.detail || err.message}`,
        );
      },
    });
  }

  stop(): void {
    this._error$.next(null);
    this.http.post<TimelapseStatusDto>(`${SERVER_URL}/timelapse/stop`, {}).subscribe({
      next: status => this.updateStatus(status),
      error: err => {
        this._error$.next(`Échec de l'arrêt du timelapse: ${err.error?.detail || err.message}`);
      },
    });
  }

  delete(metadata: TimelapseMetadata): void {
    if (!confirm(`Êtes-vous sûr de vouloir supprimer "${metadata.name}"?`)) return;

    this._error$.next(null);
    this.http.delete<void>(`${SERVER_URL}/timelapse/${metadata.id}`).subscribe({
      next: () => {
        this.store.remove(metadata.id);
        this.refreshStatus();
      },
      error: err => {
        this._error$.next(
          `Échec de la suppression du timelapse: ${err.error?.detail || err.message}`,
        );
      },
    });
  }

  private updateStatus(status: TimelapseStatusDto): void {
    const mappedStatus = mapTimelapseStatusDto(status);
    this._status$.next(mappedStatus);
    if (mappedStatus.metadata) this.store.upsert(mappedStatus.metadata);
  }
}
