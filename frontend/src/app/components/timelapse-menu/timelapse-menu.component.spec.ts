import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { NEVER } from 'rxjs';

import { TimelapseMenuComponent } from './timelapse-menu.component';
import { TimelapseWebSocketService } from '@app/services/timelapse-websocket.service';

describe('TimelapseMenuComponent', () => {
  let component: TimelapseMenuComponent;
  let fixture: ComponentFixture<TimelapseMenuComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TimelapseMenuComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: TimelapseWebSocketService, useValue: { status$: NEVER } },
      ],
    })
    .compileComponents();

    fixture = TestBed.createComponent(TimelapseMenuComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
