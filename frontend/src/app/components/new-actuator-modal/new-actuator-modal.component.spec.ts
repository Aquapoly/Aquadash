import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewActuatorModalComponent } from './new-actuator-modal.component';

describe('NewActuatorModalComponent', () => {
  let component: NewActuatorModalComponent;
  let fixture: ComponentFixture<NewActuatorModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewActuatorModalComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NewActuatorModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
