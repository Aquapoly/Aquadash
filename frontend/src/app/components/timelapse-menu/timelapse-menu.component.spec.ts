import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TimelapseMenuComponent } from './timelapse-menu.component';

describe('TimelapseMenuComponent', () => {
  let component: TimelapseMenuComponent;
  let fixture: ComponentFixture<TimelapseMenuComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TimelapseMenuComponent]
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
