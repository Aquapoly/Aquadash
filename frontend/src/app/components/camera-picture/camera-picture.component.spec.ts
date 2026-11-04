import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

import { CameraPictureComponent } from './camera-picture.component';

describe('CameraPictureComponent', () => {
  let component: CameraPictureComponent;
  let fixture: ComponentFixture<CameraPictureComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CameraPictureComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(CameraPictureComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
