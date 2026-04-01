import { Component, OnInit } from '@angular/core';
import { Pipe, PipeTransform } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { DropdownComponent, DropdownOption } from '../dropdown/dropdown.component';
import { SERVER_URL } from '@app/environment';

interface TimelapseSettings {
  frequency: DropdownOption;
  duration: DropdownOption;
  resolution: DropdownOption;
  framerate: DropdownOption;
}

@Pipe({
  name: 'filesize'
})
export class FileSizePipe implements PipeTransform {
  transform(nBytes: number): string {
    const BASE: number = 1024;
    if (nBytes < BASE) return `${nBytes.toFixed(2)} B`;
    nBytes /= BASE;
    if (nBytes < BASE) return `${nBytes.toFixed(2)} KiB`;
    nBytes /= BASE;
    if (nBytes < BASE) return `${nBytes.toFixed(2)} MiB`;
    nBytes /= BASE;
    return `${nBytes.toPrecision(2)} GiB`;
  }
}

@Pipe({
  name: 'simpleduration'
})
export class SimpleDurationPipe implements PipeTransform {
  transform(durationSeconds: number): string {
    if (durationSeconds < 5) return durationSeconds.toFixed(2) + 's';
    if (durationSeconds < 120) return durationSeconds.toFixed(0) + 's';
    
    const durationMinutes: number = Math.floor(durationSeconds / 60);
    durationSeconds = durationSeconds - durationMinutes * 60;

    return durationMinutes.toFixed(0) + 'm' + durationSeconds.toFixed(0) + 's';
  }
}

@Component({
  selector: 'app-timelapse-menu',
  imports: [CommonModule, DropdownComponent, FileSizePipe, SimpleDurationPipe],
  templateUrl: './timelapse-menu.component.html',
  styleUrl: './timelapse-menu.component.css'
})
export class TimelapseMenuComponent implements OnInit{
  timestamp: number | null = null;
  // expose SERVER_URL to the template
  readonly SERVER_URL: string = SERVER_URL;

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
      return option.value >= this.settings.frequency.value;
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

  settings: TimelapseSettings = {
    frequency: { label: '5 secondes', value: 5 },
    duration: { label: '5 secondes', value: 5 },
    resolution: { label: '640x480', value: '640x480' },
    framerate: { label: '30 par seconde', value: 30 },
  };

  running = false;
  endDate: Date | null = null;
  error: string | null = null;
  frameNumber: number = 0;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.http.get<{
      running: boolean;
      config: {frequency: number; duration: number; resolution: string} | null;
      frames_taken: number;
      expected_frames: number | null;
      end_date: number | null;
      latest_frame_time: number | null;
    }>(`${SERVER_URL}/timelapse/status`).subscribe({
      next: (response) => {
        this.running = response.running;
        if (this.running) {
          this.frameNumber = response.frames_taken;
          if (response.end_date) {
            this.endDate = new Date(response.end_date * 1000);
          }
          if (response.latest_frame_time) {
            this.timestamp = response.latest_frame_time;
          }
          if (response.config) {
            this.settings.frequency = this.frequencyOptions.find(o => o.value === response.config!.frequency) || this.settings.frequency;
            this.settings.duration = this.durationOptions.find(o => o.value === response.config!.duration) || this.settings.duration;
            this.settings.resolution = this.resolutionOptions.find(o => o.value === response.config!.resolution) || this.settings.resolution;
            this.ensureDurationValid();
          }
        }
      },
      error: (err) => {
        this.error = 'Échec de l\'obtention du statut du timelapse: ' + (err.error?.detail || err.message);
      }
    });
  }

  private ensureDurationValid(): void {
    const eligible = this.durationOptions;
    if (!eligible || eligible.length === 0) return;

    const current = this.settings.duration;
    if ((current.value as number) < (this.settings.frequency.value as number)) {
      this.settings.duration = eligible[0];
    }
  }

  getLatestFrameInfo() {
    this.http
    .get<any>(`${SERVER_URL}/timelapse/frame-info`).subscribe({
      next: (response) => {
        this.frameNumber = response.frames_taken;

        if (response.latest_frame_time) {
          this.timestamp = response.latest_frame_time; // forces image refresh
        }
      },
      error: (err) => {
        this.error =
          'Échec de l\'obtention du statut du timelapse: ' +
          (err.error?.detail || err.message);
      },
    });
  }

  onSettingChange(key: keyof TimelapseSettings, option: DropdownOption) {
    this.settings[key] = option;

    if (key === 'frequency') this.ensureDurationValid();
  }

  get expectedFrames(): number {
    return Math.floor(this.settings.duration.value as number / (this.settings.frequency.value as number)) + 1;
  }

  get expectedVidDurationSeconds(): number {
    const framerate: number = this.settings.framerate.value as number;
    const duration: number = this.expectedFrames / framerate;
    return duration;
  }

  get expectedVidSizeBytes(): number {
    // Rough empirical estimate
    const BYTES_PER_FRAME = 20 * 1024;
    return this.expectedFrames * BYTES_PER_FRAME;
  }

  get isFrequencyTooHigh(): boolean {
    return (this.settings.frequency.value as number) > (this.settings.duration.value as number);
  }

  start() {
    this.error = null;
    const payload = {
      frequency: this.settings.frequency.value,
      duration: this.settings.duration.value,
      resolution: this.settings.resolution.value,
    };

    this.http.post(`${SERVER_URL}/timelapse/start`, payload).subscribe({
      next: () => {
        this.endDate = new Date(Date.now() + (this.settings.duration.value as number) * 1000);
        this.running = true;
      },
      error: (err) => {
        this.error = `Échec du démarrage du timelapse: ${err.error?.detail || err.message}`;
      }
    });
  }

  stop() {
    this.error = null;

    this.http.post(`${SERVER_URL}/timelapse/stop`, {}).subscribe({
      next: () => {
        this.running = false;
        this.endDate = null;
        this.frameNumber = 0;
        this.timestamp = null;
      },
      error: (err) => {
        this.error = `Échec de l'arrêt du timelapse: ${err.error?.detail || err.message}`;
        this.running = false;
      }
    });
  }
}
