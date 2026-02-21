import { Component } from '@angular/core';
import { TimelapseLibraryComponent } from '@app/components/timelapse-library/timelapse-library.component';
import { TimelapseMenuComponent } from '@app/components/timelapse-menu/timelapse-menu.component';

@Component({
  selector: 'app-timelapse',
  imports: [TimelapseMenuComponent, TimelapseLibraryComponent],
  templateUrl: './timelapse.component.html',
  styleUrl: './timelapse.component.scss'
})
export class TimelapseComponent {

}
