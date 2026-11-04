import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { NEVER } from 'rxjs';
import { TimelapseWebSocketService } from '@app/services/timelapse-websocket.service';

import { TimelapsePageComponent } from './timelapse-page.component';

describe('TimelapseComponent', () => {
  let component: TimelapsePageComponent;
  let fixture: ComponentFixture<TimelapsePageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TimelapsePageComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: TimelapseWebSocketService, useValue: { status$: NEVER } },
      ],
    })
    .compileComponents();

    fixture = TestBed.createComponent(TimelapsePageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
