import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NavigationBarComponent } from './navigation-bar.component';
import { GlobalSettingsService } from '@app/services/global-settings.service/global-settings.service';
import { ChartThresholdDisplay } from '../../../constants/constants';
import { of } from 'rxjs';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

describe('NavigationBarComponent', () => {
  let component: NavigationBarComponent;
  let fixture: ComponentFixture<NavigationBarComponent>;
  let globalSettingsServiceSpy: jasmine.SpyObj<GlobalSettingsService>;

  beforeEach(async () => {
    globalSettingsServiceSpy = jasmine.createSpyObj('GlobalSettingsService', [
      'getTheme', 'applyTheme', 'toggleDarkMode'
    ]);

    globalSettingsServiceSpy.getTheme.and.returnValue(false);
    globalSettingsServiceSpy.applyTheme.and.callThrough();
    globalSettingsServiceSpy.toggleDarkMode.and.callThrough();
    
    await TestBed.configureTestingModule({
      imports: [NavigationBarComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: GlobalSettingsService, useValue: globalSettingsServiceSpy },
      ],
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(NavigationBarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
