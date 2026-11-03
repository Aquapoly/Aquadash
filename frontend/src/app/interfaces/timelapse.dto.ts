import { TimelapseConfig } from './timelapse';

export interface TimelapseMetadataDto {
  id: string;
  name: string;
  frames: number;
  framerate: number;
  start_date: string;
  latest_frame_date: string | null;
  end_date: string;
  ready: boolean | null;
  file_size_bytes?: number | null;
  preview_url?: string | null;
}

export interface TimelapseStatusDto {
  isRecording: boolean;
  metadata: TimelapseMetadataDto | null;
  config?: TimelapseConfig | null;
}
