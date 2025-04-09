import { Routes } from '@angular/router';
import { StatusPageComponent } from '@app/pages/status-page/status-page.component';
import { ConfigurationPageComponent } from '@app/pages/configuration-page/configuration-page.component';

export const routes: Routes = [
  { path: '', redirectTo: 'status', pathMatch: 'full' },
  { path: 'status', component: StatusPageComponent },
  { path: 'configurations', component: ConfigurationPageComponent },
];
