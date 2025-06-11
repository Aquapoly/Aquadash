import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LineChartComponent } from './line-chart.component';
import { SensorService } from '@app/services/sensor.service';
import { GlobalSettingsService } from '@app/services/global-settings.service/global-settings.service';
import { of } from 'rxjs';
import { ChartThresholdDisplay } from '../../../constants/constants';
import { Measurement } from '@app/interfaces/measurement';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

describe('LineChartComponent', () => {
  let component: LineChartComponent;
  let fixture: ComponentFixture<LineChartComponent>;
  let sensorServiceSpy: jasmine.SpyObj<SensorService>;
  let globalSettingsServiceSpy: jasmine.SpyObj<GlobalSettingsService>;

  beforeEach(async () => {
    sensorServiceSpy = jasmine.createSpyObj('SensorService', [
      'getSensorMeasurementsDelta',
    ]);
    
    globalSettingsServiceSpy = jasmine.createSpyObj('GlobalSettingsService', [
      'getThemeName',
    ]);

    globalSettingsServiceSpy.getThemeName.and.returnValue('light');
    globalSettingsServiceSpy.theme$ = of('light');
    globalSettingsServiceSpy.thresholdDisplay$ = of(
      {} as ChartThresholdDisplay
    );

    sensorServiceSpy.getSensorMeasurementsDelta.and.returnValue(
      Promise.resolve([] as Measurement[])
    );

    await TestBed.configureTestingModule({
      imports: [LineChartComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: SensorService, useValue: sensorServiceSpy },
        { provide: GlobalSettingsService, useValue: globalSettingsServiceSpy },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(LineChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});