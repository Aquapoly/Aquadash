import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { DropdownComponent, DropdownOption } from '../dropdown/dropdown.component';

interface TimelapseSettings {
  frequency: DropdownOption;
  duration: DropdownOption;
  resolution: DropdownOption;
}

@Component({
  selector: 'app-timelapse-menu',
  imports: [CommonModule, DropdownComponent],
  templateUrl: './timelapse-menu.component.html',
  styleUrl: './timelapse-menu.component.css'
})
export class TimelapseMenuComponent implements OnInit{
  timestamp: number | null = null;

  frequencyOptions: DropdownOption[] = [
    { label: '5 secondes', value: 5 },
    { label: '30 secondes', value: 30 },
    { label: '1 minute', value: 60 },
    { label: '1 heure', value: 3600 },
    { label: '1 jour', value: 86400 },
    { label: '2 jours', value: 172800 },
    { label: '1 semaine', value: 604800 }
  ];

  durationOptions: DropdownOption[] = [
    { label: '5 secondes', value: 5 },
    { label: '1 minute', value: 60 },
    { label: '5 minutes', value: 300 },
    { label: '15 minutes', value: 900 },
    { label: '60 minutes', value: 3600 },
    { label: '1 jour', value: 86400 },
    { label: '1 semaine', value: 604800 },
    { label: '1 mois', value: 2628000 },
  ];

  resolutionOptions: DropdownOption[] = [
    // { label: '1920x1080', value: '1920x1080' },
    // { label: '1280x720', value: '1280x720' }, Not working
    { label: '640x480', value: '640x480' },
  ];

  settings: TimelapseSettings = {
    frequency: { label: '5 secondes', value: 5 },
    duration: { label: '5 secondes', value: 5 },
    resolution: { label: '640x480', value: '640x480' },
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
    }>('http://localhost:8000/timelapse/status').subscribe({
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
          }
        }
      },
      error: (err) => {
        this.error = 'Échec de l\'obtention du statut du timelapse: ' + (err.error?.detail || err.message);
      }
    });
  }

  getLatestFrameInfo() {
    this.http
    .get<any>('http://localhost:8000/timelapse/frame-info').subscribe({
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
  }

  get expectedFrames(): number | null {
    return Math.floor(this.settings.duration.value as number / (this.settings.frequency.value as number));
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

    this.http.post('http://localhost:8000/timelapse/start', payload).subscribe({
      next: () => {
        this.endDate = new Date(Date.now() + (this.settings.duration.value as number) * 1000);
        this.running = true;
      },
      error: (err) => {
        this.error = 'Échec du démarrage du timelapse: ' + (err.error?.detail || err.message);
      }
    });
  }

  stop() {
    this.error = null;

    this.http.post('http://localhost:8000/timelapse/stop', {}).subscribe({
      next: () => {
        this.running = false;
        this.endDate = null;
        this.frameNumber = 0;
        this.timestamp = null;
      },
      error: (err) => {
        this.error = 'Échec de l\'arrêt du timelapse: ' + (err.error?.detail || err.message);
        this.running = false;
      }
    });
  }
}
