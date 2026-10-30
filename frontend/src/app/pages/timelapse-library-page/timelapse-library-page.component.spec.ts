import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TimelapseLibraryComponent } from './timelapse-library.component';

describe('TimelapseLibraryPageComponent', () => {
  let component: TimelapseComponent;
  let fixture: ComponentFixture<TimelapseComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TimelapseComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TimelapseComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
