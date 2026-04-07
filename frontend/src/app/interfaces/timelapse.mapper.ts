import { TimelapseMetadata, TimelapseStatus } from './timelapse';
import { TimelapseMetadataDto, TimelapseStatusDto } from './timelapse.dto';

export function mapTimelapseMetadataDto(dto: TimelapseMetadataDto): TimelapseMetadata {
  return {
    ...dto,
    start_date: new Date(dto.start_date),
    end_date: new Date(dto.end_date),
    latest_frame_date: dto.latest_frame_date ? new Date(dto.latest_frame_date) : null,
  };
}

export function mapTimelapseStatusDto(dto: TimelapseStatusDto): TimelapseStatus {
  return {
    ...dto,
    metadata: dto.metadata ? mapTimelapseMetadataDto(dto.metadata) : null,
  };
}
