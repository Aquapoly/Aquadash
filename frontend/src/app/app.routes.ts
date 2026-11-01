import { Routes } from '@angular/router';
import { StatusPageComponent } from '@app/pages/status-page/status-page.component';
import { ConfigurationPageComponent } from '@app/pages/configuration-page/configuration-page.component';
import { Time } from 'highcharts';
import { TimelapsePageComponent } from './pages/timelapse-page/timelapse-page.component';
import { TimelapseLibraryPageComponent } from './pages/timelapse-library-page/timelapse-library-page.component';
import { LoginComponent } from '@app/account/login.component'; 
 
export const routes: Routes = [
  { path: '', redirectTo: 'status', pathMatch: 'full' },
  { path: 'status', component: StatusPageComponent },
  { path: 'configurations', component: ConfigurationPageComponent },
  { path: 'timelapse', component: TimelapsePageComponent },
  { path: 'timelapse-library', component: TimelapseLibraryPageComponent },
  { path: 'login', component: LoginComponent },
];
