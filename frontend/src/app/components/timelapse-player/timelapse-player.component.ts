import { Component, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SERVER_URL } from '@app/environment';
import { TimelapseMetadata } from '@app/interfaces/timelapse';

@Component({
  selector: 'app-timelapse-player',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './timelapse-player.component.html',
  styleUrl: './timelapse-player.component.scss'
})
export class TimelapsePlayerComponent {
  @ViewChild('videoDialog') private videoDialog!: ElementRef<HTMLDialogElement>;

  selectedTimelapse: TimelapseMetadata | null = null;
  videoError = false;

  open(timelapse: TimelapseMetadata): void {
    this.selectedTimelapse = timelapse;
    this.videoError = false;
    this.videoDialog.nativeElement.showModal();
  }

  videoUrl(timelapse: TimelapseMetadata): string {
    return `${SERVER_URL}/timelapse/${timelapse.id}/video`;
  }

  onVideoError(): void {
    this.videoError = true;
  }

  close(): void {
    this.videoDialog.nativeElement.close();
    this.reset();
  }

  onDialogClose(): void {
    this.reset();
  }

  onDialogClick(event: MouseEvent): void {
    if (event.target === this.videoDialog.nativeElement) {
      this.close();
    }
  }

  private reset(): void {
    this.selectedTimelapse = null;
    this.videoError = false;
  }
}
