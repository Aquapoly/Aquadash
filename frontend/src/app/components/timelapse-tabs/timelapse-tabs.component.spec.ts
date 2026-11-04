import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { TimelapseTabsComponent } from './timelapse-tabs.component';

describe('TimelapseTabsComponent', () => {
  let component: TimelapseTabsComponent;
  let fixture: ComponentFixture<TimelapseTabsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TimelapseTabsComponent],
      providers: [provideRouter([])],
    })
    .compileComponents();

    fixture = TestBed.createComponent(TimelapseTabsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
