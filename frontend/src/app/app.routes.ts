import { Routes } from '@angular/router';
import { StatusPageComponent } from '@app/pages/status-page/status-page.component';
import { ConfigurationPageComponent } from '@app/pages/configuration-page/configuration-page.component';
import { Time } from 'highcharts';
import { TimelapseComponent } from './pages/timelapse/timelapse.component';
import { LoginComponent } from '@app/account/login.component'; 
import { RegisterComponent } from '@app/account/register.component';
 
export const routes: Routes = [
  { path: '', redirectTo: 'status', pathMatch: 'full' },
  { path: 'status', component: StatusPageComponent },
  { path: 'configurations', component: ConfigurationPageComponent },
  { path: 'timelapse', component: TimelapseComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent }
];
