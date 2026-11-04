import { Injectable } from '@angular/core';
import { Observable, filter, map, share } from 'rxjs';
import { SERVER_URL } from '@app/environment';
import { TimelapseStatusDto } from '@app/interfaces/timelapse.dto';
import { WebSocketService } from '@app/services/websocket.service';

const WS_URL = SERVER_URL.replace(/^http/, 'ws') + '/ws/timelapse';

@Injectable({ providedIn: 'root' })
export class TimelapseWebSocketService {
  /** Stream of timelapse status events pushed by the backend. */
  readonly status$: Observable<TimelapseStatusDto>;

  constructor(webSocketService: WebSocketService) {
    this.status$ = webSocketService.connect(WS_URL).pipe(
      map(parseTimelapseStatus),
      filter((status): status is TimelapseStatusDto => status !== null),
      share(),
    );
  }
}

function parseTimelapseStatus(message: unknown): TimelapseStatusDto | null {
  return isTimelapseStatusDto(message) ? message : invalidStatus(message);
}

function isTimelapseStatusDto(message: unknown): message is TimelapseStatusDto {
  if (!isRecord(message) || typeof message['is_recording'] !== 'boolean') return false;

  const metadata = message['metadata'];
  if (
    metadata !== null &&
    (!isRecord(metadata) ||
      typeof metadata['id'] !== 'string' ||
      typeof metadata['name'] !== 'string' ||
      typeof metadata['frames'] !== 'number' ||
      typeof metadata['framerate'] !== 'number' ||
      typeof metadata['start_date'] !== 'string' ||
      typeof metadata['end_date'] !== 'string' ||
      !(metadata['latest_frame_date'] === null ||
        typeof metadata['latest_frame_date'] === 'string') ||
      !(metadata['ready'] === null || typeof metadata['ready'] === 'boolean'))
  ) {
    return false;
  }

  const config = message['config'];
  if (
    config !== undefined &&
    config !== null &&
    (!isRecord(config) ||
      typeof config['frequency'] !== 'number' ||
      typeof config['duration'] !== 'number' ||
      typeof config['framerate'] !== 'number' ||
      !(config['name'] === undefined || config['name'] === null || typeof config['name'] === 'string'))
  ) {
    return false;
  }

  return true;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function invalidStatus(message: unknown): null {
  console.warn('[TimelapseWS] Received an invalid status message:', message);
  return null;
}
