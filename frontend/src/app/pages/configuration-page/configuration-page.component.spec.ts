import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ConfigurationPageComponent as ConfigurationPageComponent } from './configuration-page.component';

describe('ActuatorPageComponent', () => {
  let component: ConfigurationPageComponent;
  let fixture: ComponentFixture<ConfigurationPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ConfigurationPageComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ConfigurationPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
