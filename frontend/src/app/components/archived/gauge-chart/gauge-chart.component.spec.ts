import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GaugeChartComponent } from './gauge-chart.component';
import { GlobalSettingsService } from '@app/services/global-settings.service/global-settings.service';
import { of } from 'rxjs';
import { ChartThresholdDisplay } from '../../../constants/constants';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

describe('GaugeChartComponent', () => {
  let component: GaugeChartComponent;
  let fixture: ComponentFixture<GaugeChartComponent>;
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
      imports: [GaugeChartComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: GlobalSettingsService, useValue: globalSettingsServiceSpy },
      ],
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(GaugeChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
