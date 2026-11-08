import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DurationPipe } from '@app/classes/duration';
import { SERVER_URL } from '@app/environment';
import { TimelapseStatus } from '@app/interfaces/timelapse';
import { TimelapseSessionService } from '@app/services/timelapse-session.service';

@Component({
  selector: 'app-timelapse-record-panel',
  standalone: true,
  imports: [CommonModule, DurationPipe],
  templateUrl: './timelapse-record-panel.component.html',
  styleUrl: './timelapse-record-panel.component.scss'
})
export class TimelapseRecordPanelComponent {
  @Input() compact = false;

  constructor(private readonly session: TimelapseSessionService) {}

  get status$() {
    return this.session.status$;
  }

  get error$() {
    return this.session.error$;
  }

  expectedFrames(status: TimelapseStatus): number {
    const { duration, frequency } = status.config ?? {};
    if (!duration || !frequency || duration < frequency) return 0;
    return Math.floor(duration / frequency) + 1;
  }

  thumbnailUrl(status: TimelapseStatus): string | null {
    const latestFrameDate = status.metadata?.latest_frame_date;
    return latestFrameDate
      ? `${SERVER_URL}/timelapse/latest-frame?t=${latestFrameDate.getTime()}`
      : null;
  }

  progress(status: TimelapseStatus): number {
    const expected = this.expectedFrames(status);
    if (!expected) return 0;
    const frames = status.metadata?.frames ?? 0;
    return Math.min(100, Math.round((frames / expected) * 100));
  }

  remainingSeconds(status: TimelapseStatus): number {
    const end = status.metadata?.end_date;
    if (!end) return 0;
    return Math.max(0, Math.round((end.getTime() - Date.now()) / 1000));
  }

  stop(): void {
    this.session.stop();
  }

  delete(status: TimelapseStatus): void {
    if (status.metadata) this.session.delete(status.metadata);
  }
}
