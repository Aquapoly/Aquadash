import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { NEVER } from 'rxjs';

import { TimelapseRecordPanelComponent } from './timelapse-record-panel.component';
import { TimelapseWebSocketService } from '@app/services/timelapse-websocket.service';

describe('TimelapseRecordPanelComponent', () => {
  let component: TimelapseRecordPanelComponent;
  let fixture: ComponentFixture<TimelapseRecordPanelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TimelapseRecordPanelComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: TimelapseWebSocketService, useValue: { status$: NEVER } },
      ],
    })
    .compileComponents();

    fixture = TestBed.createComponent(TimelapseRecordPanelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
