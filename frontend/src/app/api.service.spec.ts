import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HttpClient, HttpResponse, provideHttpClient } from '@angular/common/http';
import { HttpClientTestingModule, HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { of } from 'rxjs/internal/observable/of';
import { ApiService } from './services/api.service';

describe('ApiService', () => {
  let component: ApiService;
  let fixture: ComponentFixture<ApiService>;
  let httpClientSpy: jasmine.SpyObj<HttpClient>;
  let httpTest: HttpTestingController;
  let apiService: ApiService;

  beforeEach(() => {
    httpClientSpy = jasmine.createSpyObj('HttpClient', [
      'get', 'patch'
    ]);

    httpClientSpy.get.and.returnValues(of('{}'));
    httpClientSpy.patch.and.returnValue(of('{}'))

    TestBed.configureTestingModule({
      imports: [ApiService],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        {provide: HttpClient, useValue: httpClientSpy}
      ],
    }).compileComponents();

    httpTest = TestBed.inject(HttpTestingController);


    fixture = TestBed.createComponent(ApiService);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
