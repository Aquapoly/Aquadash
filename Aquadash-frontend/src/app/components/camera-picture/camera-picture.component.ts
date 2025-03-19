import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { SERVER_URL } from '@app/environment';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faRotate } from '@fortawesome/free-solid-svg-icons';



@Component({
  selector: 'app-camera-picture',
  standalone: true,
  imports: [FontAwesomeModule],
  templateUrl: './camera-picture.component.html',
  styleUrl: './camera-picture.component.scss'
})
export class CameraPictureComponent implements OnInit, OnDestroy {
  @Input() url: string = '';
  id?: number;
  faReload = faRotate;
  static readonly RELOAD_TIME_MS = 10000;

  reloadPicture() {
    if (!document.hidden) {
      this.url = `${SERVER_URL}/picture?_ts=${Date.now()}`;
    }
  }

  onReloadClick() {
    if (this.id) {
      clearInterval(this.id);
    }

    this.reloadPicture();
    this.id = setInterval(() => this.reloadPicture(), CameraPictureComponent.RELOAD_TIME_MS);
  }

  ngOnInit() {
    this.reloadPicture();
    this.id = setInterval(() => this.reloadPicture(), CameraPictureComponent.RELOAD_TIME_MS);
  }

  ngOnDestroy() {
    if (this.id) {
      clearInterval(this.id);
      this.id = undefined;
    }
  }
}
