import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CameraPictureComponent } from './camera-picture.component';

describe('CameraPictureComponent', () => {
  let component: CameraPictureComponent;
  let fixture: ComponentFixture<CameraPictureComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CameraPictureComponent]
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
