import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from '@app/app.config';
import { AppComponent } from '@app/pages/app/app.component';
import * as Highcharts from 'highcharts';

Highcharts.setOptions({
  time: {
    timezone: 'America/Toronto',
  },
});

bootstrapApplication(AppComponent, appConfig).catch((err) =>
  console.error(err),
);
