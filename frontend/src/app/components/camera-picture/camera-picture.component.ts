import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { SERVER_URL } from '@app/environment';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faRotate } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-camera-picture',
  standalone: true,
  imports: [FontAwesomeModule],
  templateUrl: './camera-picture.component.html',
  styleUrl: './camera-picture.component.scss',
})
export class CameraPictureComponent implements OnInit, OnDestroy {
  @Input() url: string = '';
  faReload = faRotate;
  private id?: ReturnType<typeof setInterval>;
  private static readonly RELOAD_TIME_MS = 10000;

  ngOnInit() {
    this.reloadTimeout();
  }

  ngOnDestroy() {
    if (this.id) {
      clearInterval(this.id);
      this.id = undefined;
    }
  }

  onReloadClick() {
    if (this.id) {
      clearInterval(this.id);
    }

    this.reloadTimeout();
  }

  private reloadPicture() {
    if (!document.hidden) {
      this.url = `${SERVER_URL}/picture?_ts=${Date.now()}`;
    }
  }

  private reloadTimeout() {
    this.reloadPicture();
    this.id = setInterval(
      () => this.reloadPicture(),
      CameraPictureComponent.RELOAD_TIME_MS
    );
  }
}
