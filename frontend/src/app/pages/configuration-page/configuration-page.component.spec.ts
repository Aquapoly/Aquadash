import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ConfigurationPageComponent as ConfigurationPageComponent } from './configuration-page.component';
import { HttpResponse, provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { ApiService } from '@app/services/api.service';
import { of } from 'rxjs/internal/observable/of';

describe('ActuatorPageComponent', () => {
  let component: ConfigurationPageComponent;
  let fixture: ComponentFixture<ConfigurationPageComponent>;
  let apiServiceSpy: jasmine.SpyObj<ApiService>;

  beforeEach(async () => {
    // apiServiceSpy = jasmine.createSpyObj('ApiService', [
    //   'getActuators', 'patchActuators'
    // ]);

    // apiServiceSpy.getActuators.and.returnValue(of(
    //   {} as HttpResponse<Object>
    // ));

    // apiServiceSpy.patchActuators.and.returnValue(of(
    //   {} as HttpResponse<Object>
    // ));

    await TestBed.configureTestingModule({
      imports: [ConfigurationPageComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        // { provide: ApiService, useValue: apiServiceSpy },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ConfigurationPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
