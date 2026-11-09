import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ModifyActuatorModalComponent } from './modify-actuator-modal.component';

describe('ModifyActuatorModalComponent', () => {
  let component: ModifyActuatorModalComponent;
  let fixture: ComponentFixture<ModifyActuatorModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ModifyActuatorModalComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ModifyActuatorModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
