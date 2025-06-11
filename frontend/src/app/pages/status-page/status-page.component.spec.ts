import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StatusPageComponent } from './status-page.component';
import { GlobalSettingsService } from '@app/services/global-settings.service/global-settings.service';
import { ChartThresholdDisplay } from '../../../constants/constants';
import { of } from 'rxjs';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

describe('StatusPageComponent', () => {
  let component: StatusPageComponent;
  let fixture: ComponentFixture<StatusPageComponent>;
  let globalSettingsServiceSpy: jasmine.SpyObj<GlobalSettingsService>;

  beforeEach(async () => {

    globalSettingsServiceSpy = jasmine.createSpyObj('GlobalSettingsService', [
      'getThemeName',
    ]);

    globalSettingsServiceSpy.getThemeName.and.returnValue('light');
    globalSettingsServiceSpy.theme$ = of('light');
    globalSettingsServiceSpy.thresholdDisplay$ = of(
      {} as ChartThresholdDisplay
    );
    
    await TestBed.configureTestingModule({
      imports: [StatusPageComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: GlobalSettingsService, useValue: globalSettingsServiceSpy },
      ],
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(StatusPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
