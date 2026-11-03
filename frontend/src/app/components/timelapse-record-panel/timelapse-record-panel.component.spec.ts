import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TimelapseRecordPanelComponent } from './timelapse-record-panel.component';

describe('TimelapseRecordPanelComponent', () => {
  let component: TimelapseRecordPanelComponent;
  let fixture: ComponentFixture<TimelapseRecordPanelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TimelapseRecordPanelComponent]
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
