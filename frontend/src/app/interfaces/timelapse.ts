export interface TimelapseConfig {
    frequency: number;
    duration: number;
    // TODO: add resolution
    framerate: number;
    name: string | undefined;
}

export interface TimelapseMetadata {
    id: string;
    name: string;
    frames: number;
    framerate: number;
    start_date: Date;
    latest_frame_date: Date | null;
    end_date: Date;
    ready: boolean | null;
}

export interface TimelapseStatus {
    running: boolean;
    metadata: TimelapseMetadata | null;
    config?: TimelapseConfig | null;
}