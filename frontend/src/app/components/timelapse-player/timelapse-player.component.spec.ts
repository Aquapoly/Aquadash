import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { NEVER } from 'rxjs';

import { TimelapsePlayerComponent } from './timelapse-player.component';
import { TimelapseWebSocketService } from '@app/services/timelapse-websocket.service';

describe('TimelapsePlayerComponent', () => {
  let component: TimelapsePlayerComponent;
  let fixture: ComponentFixture<TimelapsePlayerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TimelapsePlayerComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: TimelapseWebSocketService, useValue: { status$: NEVER } },
      ],
    })
    .compileComponents();

    fixture = TestBed.createComponent(TimelapsePlayerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
