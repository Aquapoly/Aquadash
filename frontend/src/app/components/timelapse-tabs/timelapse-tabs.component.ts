import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-timelapse-tabs',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './timelapse-tabs.component.html',
  styleUrl: './timelapse-tabs.component.scss'
})
export class TimelapseTabsComponent {}
