import { Routes } from '@angular/router';
import { StatusPageComponent } from '@app/pages/status-page/status-page.component';
import { SettingsPageComponent } from './pages/settings-page/settings-page.component';

export const routes: Routes = [
    { path: '', redirectTo: 'status', pathMatch: 'full' },
    { path: 'status', component: StatusPageComponent },
    { path: 'settings', component: SettingsPageComponent}
];
