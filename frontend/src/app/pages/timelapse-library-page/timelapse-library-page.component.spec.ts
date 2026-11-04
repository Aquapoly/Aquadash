import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { TimelapseLibraryComponent } from '@app/components/timelapse-library/timelapse-library.component';

describe('TimelapseLibraryPageComponent', () => {
  let component: TimelapseLibraryComponent;
  let fixture: ComponentFixture<TimelapseLibraryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TimelapseLibraryComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
      ],
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
