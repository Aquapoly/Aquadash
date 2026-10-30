import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Subscription } from 'rxjs';
import { DropdownComponent, DropdownOption } from '@app/components/dropdown/dropdown.component';
import { DurationPipe } from '@app/classes/duration';
import { TimelapseConfig, TimelapseStatus } from '@app/interfaces/timelapse';
import { TimelapseStoreService } from '@app/services/timelapse-store.service';
import { TimelapseStatusDto } from '@app/interfaces/timelapse.dto';
import { mapTimelapseStatusDto } from '@app/interfaces/timelapse.mapper';
import { TimelapseWebSocketService } from '@app/services/timelapse-websocket.service';
import { SERVER_URL } from '@app/environment';

interface TimeUnit {
  label: string;
  value: number;
}

interface TimePreset {
  label: string;
  value: number;
  unitValue: number;
}

@Component({
  selector: 'app-timelapse-menu',
  imports: [CommonModule, DropdownComponent, DurationPipe],
  templateUrl: './timelapse-menu.component.html',
  styleUrl: './timelapse-menu.component.css'
})
export class TimelapseMenuComponent implements OnInit, OnDestroy {
  private wsSub: Subscription | null = null;

  readonly timeUnits: TimeUnit[] = [
    { label: 's', value: 1 },
    { label: 'min', value: 60 },
    { label: 'h', value: 3600 },
    { label: 'jr', value: 86400 },
    { label: 'sem', value: 604800 },
  ];
  readonly durationPresets: TimePreset[] = [
    { label: '10 min', value: 10, unitValue: 60 },
    { label: '1 h', value: 1, unitValue: 3600 },
    { label: '1 jr', value: 1, unitValue: 86400 },
  ];
  readonly frequencyPresets: TimePreset[] = [
    { label: '10 s', value: 10, unitValue: 1 },
    { label: '30 s', value: 30, unitValue: 1 },
    { label: '1 min', value: 1, unitValue: 60 },
  ];
  readonly framerateOptions: DropdownOption[] = [
    { label: '10 par seconde', value: 10 },
    { label: '20 par seconde', value: 20 },
    { label: '30 par seconde', value: 30 },
  ];

  durationValue = 10;
  durationUnit = this.timeUnits[1];
  frequencyValue = 10;
  frequencyUnit = this.timeUnits[0];
  framerate: DropdownOption = this.framerateOptions[2];

  private status_: TimelapseStatus | null = null;
  error: string | null = null;

  get status(): TimelapseStatus | null {
    return this.status_;
  }

  private set status(value: TimelapseStatus | null) {
    this.status_ = value;
  }

  get isRecording(): boolean {
    return this.status?.isRecording ?? false;
  }

  get durationSeconds(): number {
    return this.durationValue * this.durationUnit.value;
  }

  get frequencySeconds(): number {
    return this.frequencyValue * this.frequencyUnit.value;
  }

  get hasValidSettings(): boolean {
    return Number.isInteger(this.durationValue) &&
      Number.isInteger(this.frequencyValue) &&
      this.durationValue > 0 &&
      this.frequencyValue > 0 &&
      this.frequencySeconds <= this.durationSeconds;
  }

  get isFrequencyTooHigh(): boolean {
    return this.frequencyValue > 0 &&
      this.durationValue > 0 &&
      this.frequencySeconds > this.durationSeconds;
  }

  get expectedFrames(): number {
    return this.hasValidSettings
      ? Math.floor(this.durationSeconds / this.frequencySeconds) + 1
      : 0;
  }

  get expectedVidDurationSeconds(): number {
    return this.expectedFrames / Number(this.framerate.value);
  }

  get expectedVidSizeMegabytes(): number {
    const bytesPerFrame = 20 * 1024;
    return Math.round((this.expectedFrames * bytesPerFrame) / (1024 * 1024));
  }

  get thumbnailUrl(): string | null {
    const latestFrameDate = this.status?.metadata?.latest_frame_date;
    return latestFrameDate
      ? `${SERVER_URL}/timelapse/latest-frame?t=${latestFrameDate.getTime()}`
      : null;
  }

  constructor(
    private http: HttpClient,
    private store: TimelapseStoreService,
    private wsService: TimelapseWebSocketService,
  ) {}

  ngOnInit(): void {
    this.getStatus();
    this.wsSub = this.wsService.status$.subscribe((dto: TimelapseStatusDto) => {
      this.updateStatus(dto);
    });
  }

  ngOnDestroy(): void {
    this.wsSub?.unsubscribe();
  }

  setDurationValue(event: Event): void {
    if (event.target instanceof HTMLInputElement) {
      this.durationValue = Number(event.target.value);
    }
  }

  setFrequencyValue(event: Event): void {
    if (event.target instanceof HTMLInputElement) {
      this.frequencyValue = Number(event.target.value);
    }
  }

  setDurationUnit(event: Event): void {
    if (!(event.target instanceof HTMLSelectElement)) return;
    const value = Number(event.target.value);
    const unit = this.timeUnits.find(option => option.value === value);
    if (unit) this.durationUnit = unit;
  }

  setFrequencyUnit(event: Event): void {
    if (!(event.target instanceof HTMLSelectElement)) return;
    const value = Number(event.target.value);
    const unit = this.timeUnits.find(option => option.value === value);
    if (unit) this.frequencyUnit = unit;
  }

  setDurationPreset(preset: TimePreset): void {
    this.durationValue = preset.value;
    this.durationUnit = this.timeUnits.find(unit => unit.value === preset.unitValue) ?? this.timeUnits[0];
  }

  setFrequencyPreset(preset: TimePreset): void {
    this.frequencyValue = preset.value;
    this.frequencyUnit = this.timeUnits.find(unit => unit.value === preset.unitValue) ?? this.timeUnits[0];
  }

  isDurationPresetSelected(preset: TimePreset): boolean {
    return this.durationSeconds === preset.value * preset.unitValue;
  }

  isFrequencyPresetSelected(preset: TimePreset): boolean {
    return this.frequencySeconds === preset.value * preset.unitValue;
  }

  onFramerateChange(option: DropdownOption): void {
    this.framerate = option;
  }

  private restoreSettingsFromStatus(status: TimelapseStatus): void {
    const config = status.config;
    if (!config) return;

    this.restoreTimeValue(config.duration, 'duration');
    this.restoreTimeValue(config.frequency, 'frequency');
    const framerate = this.framerateOptions.find(option => option.value === config.framerate);
    if (framerate) this.framerate = framerate;
  }

  private restoreTimeValue(seconds: number, setting: 'frequency' | 'duration'): void {
    const unit = [...this.timeUnits].reverse().find(option => seconds % option.value === 0)
      ?? this.timeUnits[0];
    const value = seconds / unit.value;

    if (setting === 'duration') {
      this.durationValue = value;
      this.durationUnit = unit;
    } else {
      this.frequencyValue = value;
      this.frequencyUnit = unit;
    }
  }

  private getStatus(): void {
    this.http.get<TimelapseStatusDto>(`${SERVER_URL}/timelapse/status`).subscribe({
      next: (response: TimelapseStatusDto) => {
        this.updateStatus(response);
        if (this.status?.isRecording) this.restoreSettingsFromStatus(this.status);
      },
      error: (err) => {
        this.error =
          `Échec de l'obtention du statut du timelapse: ${err.error?.detail || err.message}`;
      },
    });
  }

  start(): void {
    this.error = null;
    if (!this.hasValidSettings) return;

    const payload: TimelapseConfig = {
      frequency: this.frequencySeconds,
      duration: this.durationSeconds,
      framerate: Number(this.framerate.value),
      name: undefined,
    };

    this.http.post<TimelapseStatusDto>(`${SERVER_URL}/timelapse/start`, payload).subscribe({
      next: (status: TimelapseStatusDto) => {
        this.updateStatus(status);
        if (this.status?.isRecording) this.restoreSettingsFromStatus(this.status);
      },
      error: (err) => {
        this.error = `Échec du démarrage du timelapse: ${err.error?.detail || err.message}`;
      }
    });
  }

  stop(): void {
    this.error = null;
    this.http.post<TimelapseStatusDto>(`${SERVER_URL}/timelapse/stop`, {}).subscribe({
      next: (status: TimelapseStatusDto) => {
        if (this.status?.metadata) this.store.upsert({ ...this.status.metadata, ready: true });
        this.updateStatus(status);
      },
      error: (err) => {
        this.error = `Échec de l'arrêt du timelapse: ${err.error?.detail || err.message}`;
      }
    });
  }

  private updateStatus(status: TimelapseStatusDto): void {
    this.status = mapTimelapseStatusDto(status);
    const metadata = this.status?.metadata;
    if (metadata) this.store.upsert(metadata);
  }
}
