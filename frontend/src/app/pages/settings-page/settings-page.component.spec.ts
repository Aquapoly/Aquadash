import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SettingsPageComponent as SettingsPageComponent } from './settings-page.component';

describe('ActuatorPageComponent', () => {
  let component: SettingsPageComponent;
  let fixture: ComponentFixture<SettingsPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SettingsPageComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(SettingsPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
