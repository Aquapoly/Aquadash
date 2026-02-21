import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TimelapseLibraryComponent } from './timelapse-library.component';

describe('TimelapseLibraryComponent', () => {
  let component: TimelapseLibraryComponent;
  let fixture: ComponentFixture<TimelapseLibraryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TimelapseLibraryComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TimelapseLibraryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
