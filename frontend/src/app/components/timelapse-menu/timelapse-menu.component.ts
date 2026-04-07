import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { DropdownComponent, DropdownOption } from '@app/components/dropdown/dropdown.component';
import { SERVER_URL } from '@app/environment';

import { FileSizePipe } from '@app/classes/filesize';
import { DurationPipe } from '@app/classes/duration';
import { TimelapseConfig, TimelapseStatus } from '@app/interfaces/timelapse';
import { TimelapseStoreService } from '@app/services/timelapse-store.service';
import { TimelapseStatusDto } from '@app/interfaces/timelapse.dto';
import { mapTimelapseStatusDto } from '@app/interfaces/timelapse.mapper';

interface TimelapseSettings {
  frequency: DropdownOption;
  duration: DropdownOption;
  resolution: DropdownOption;
  framerate: DropdownOption;
  // name: string | null;
}

@Component({
  selector: 'app-timelapse-menu',
  imports: [CommonModule, DropdownComponent, FileSizePipe, DurationPipe],
  templateUrl: './timelapse-menu.component.html',
  styleUrl: './timelapse-menu.component.css'
})
export class TimelapseMenuComponent implements OnInit{
  timestamp: Date | null = null;

  readonly frequencyOptions: DropdownOption[] = [
    { label: '5 secondes', value: 5 },
    { label: '30 secondes', value: 30 },
    { label: '1 minute', value: 60 },
    { label: '1 heure', value: 3600 },
    { label: '1 jour', value: 86400 },
    { label: '2 jours', value: 172800 },
    { label: '1 semaine', value: 604800 }
  ];

  private readonly durationOptions_: DropdownOption[] = [
    { label: '5 secondes', value: 5 },
    { label: '1 minute', value: 60 },
    { label: '5 minutes', value: 300 },
    { label: '15 minutes', value: 900 },
    { label: '60 minutes', value: 3600 },
    { label: '1 jour', value: 86400 },
    { label: '1 semaine', value: 604800 },
    { label: '1 mois', value: 2628000 },
  ];

  get durationOptions(): DropdownOption[] {
    return this.durationOptions_.filter((option: DropdownOption) => {
      return option.value >= this.frequency.value;
    });
  }

  readonly resolutionOptions: DropdownOption[] = [
    // { label: '1920x1080', value: '1920x1080' },
    // { label: '1280x720', value: '1280x720' }, Not working
    { label: '640x480', value: '640x480' },
  ];

  readonly framerateOptions: DropdownOption[] = [
    { label: '10 par seconde', value: 10 },
    { label: '20 par seconde', value: 20 },
    { label: '30 par seconde', value: 30 },
  ];

  private settings: TimelapseSettings = {
    frequency: { label: '5 secondes', value: 5 },
    duration: { label: '5 secondes', value: 5 },
    resolution: { label: '640x480', value: '640x480' },
    framerate: { label: '30 par seconde', value: 30 },
  };

  get frequency(): DropdownOption {
    return this.settings.frequency;
  }
  private set frequency(value: DropdownOption) {
    this.settings.frequency = value;
  }
  
  get duration(): DropdownOption {
    return this.settings.duration;
  }
  private set duration(value: DropdownOption) {
    this.settings.duration = value;
  }

  get resolution(): DropdownOption {
    return this.settings.resolution;
  }
  private set resolution(value: DropdownOption) {
    this.settings.resolution = value;
  }

  get framerate(): DropdownOption {
    return this.settings.framerate;
  }
  private set framerate(value: DropdownOption) {
    this.settings.framerate = value;
  }

  private status_: TimelapseStatus | null = null;
  error: string | null = null;
  get status(): TimelapseStatus | null {
    return this.status_;
  }
  private set status(value: TimelapseStatus | null) {
    this.status_ = value;
  }

  get running(): boolean {
    return this.status?.running ?? false;
  }

  get thumbnailUrl(): string | null {
    return this.timestamp ? `${SERVER_URL}/timelapse/latest-frame?t=${this.timestamp.getTime()}` : null;
  }

  constructor(private http: HttpClient, private store: TimelapseStoreService) {}

  private restoreSettingsFromStatus(status: TimelapseStatus): void {
    const cfg = status?.config;
    if (!cfg) return;

    const freqOpt = this.frequencyOptions.find(o => o.value === cfg.frequency);
    if (freqOpt) this.frequency = freqOpt;

    const durOpt = this.durationOptions_.find(o => o.value === cfg.duration);
    if (durOpt) this.duration = durOpt;

    const frOpt = this.framerateOptions.find(o => o.value === cfg.framerate);
    if (frOpt) this.framerate = frOpt;

    this.ensureDurationValid();
  }

  ngOnInit(): void {
    this.getStatus();
  }

  private ensureDurationValid(): void {
    const eligible = this.durationOptions;
    if (!eligible || eligible.length === 0) return;

    const current: DropdownOption = this.duration;
    if (current.value < this.frequency.value) this.duration = eligible[0];
  }

  getStatus() {
    this.http
    .get<TimelapseStatusDto>(`${SERVER_URL}/timelapse/status`).subscribe({
      next: (response: TimelapseStatusDto) => {
        this.updateStatus(response);

        if (this.status?.running) {
          this.restoreSettingsFromStatus(this.status);
          this.timestamp = new Date();
        } else {
          this.timestamp = null;
        }
      },
      error: (err) => {
        this.error =
          `Échec de l'obtention du statut du timelapse: ${err.error?.detail || err.message}`;
      },
    });
  }

  onSettingChange(key: keyof TimelapseSettings, option: DropdownOption) {
    this.settings[key] = option;
    if (key === 'frequency') this.ensureDurationValid();
  }

  get expectedFrames(): number {
    return Math.floor((this.duration.value as number) / (this.frequency.value as number)) + 1;
  }

  get expectedVidDurationSeconds(): number {
    const framerate: number = this.framerate.value as number;
    const duration: number = this.expectedFrames / framerate;
    return duration;
  }

  get expectedVidSizeBytes(): number {
    // Rough empirical estimate
    const BYTES_PER_FRAME: number = 20 * 1024;
    return this.expectedFrames * BYTES_PER_FRAME;
  }

  get isFrequencyTooHigh(): boolean {
    return this.frequency.value > this.duration.value;
  }

  start() {
    this.error = null;
    const payload: TimelapseConfig = {
      frequency: this.frequency.value as number,
      duration: this.duration.value as number,
      // resolution: this.resolution.value,
      framerate: this.framerate.value as number,
      name: undefined,
    };

    this.http.post<TimelapseStatusDto>(`${SERVER_URL}/timelapse/start`, payload).subscribe({
      next: (status: TimelapseStatusDto) => {
        this.updateStatus(status);
        if (this.status?.running) this.restoreSettingsFromStatus(this.status);
      },
      error: (err) => {
        this.error = `Échec du démarrage du timelapse: ${err.error?.detail || err.message}`;
      }
    });
  }

  stop() {
    this.error = null;

    this.http.post<TimelapseStatusDto>(`${SERVER_URL}/timelapse/stop`, {}).subscribe({
      next: (status: TimelapseStatusDto) => {
        if (this.status?.metadata) this.store.upsert({...this.status.metadata, ready: true});
        this.updateStatus(status);
      },
      error: (err) => {
        this.error = `Échec de l'arrêt du timelapse: ${err.error?.detail || err.message}`;
      }
    });
  }

  private updateStatus(status: TimelapseStatusDto) {
    this.status = mapTimelapseStatusDto(status);
    const metadata = this.status?.metadata;
    if (metadata) this.store.upsert(metadata);
  }
}
