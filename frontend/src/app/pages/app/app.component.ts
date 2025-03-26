import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NavigationBarComponent } from '@app/components/navigation-bar/navigation-bar.component';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { LineChartComponent } from '@app/components/line-chart/line-chart.component';
import { StatusPageComponent } from '@app/pages/status-page/status-page.component';
import { SettingsPageComponent } from '@app/pages/settings-page/settings-page.component';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, NavigationBarComponent, FontAwesomeModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  title = 'aquadash';
}
