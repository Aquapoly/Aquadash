import { Component, OnInit, OnDestroy } from '@angular/core';
import { SERVER_URL } from '@app/environment';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-camera-picture',
  standalone: true,
  templateUrl: './camera-picture.component.html',
  styleUrl: './camera-picture.component.scss',
})
export class CameraPictureComponent implements OnInit, OnDestroy {
  private static readonly RELOAD_TIME_MS = 10000;
  private url: URL = new URL('/picture', SERVER_URL);
  private id?: ReturnType<typeof setInterval>;

  // object URL currently shown by the <img>
  _displayedObjectUrl?: string;
  // last successfully loaded image object URL (cached)
  private cachedObjectUrl?: string;

  private _isCameraAvailable = true;

  constructor(private http: HttpClient) {}

  get isCameraAvailable(): boolean {
    return this._isCameraAvailable;
  }

  get displayedObjectUrl(): string | undefined {
    return this._displayedObjectUrl;
  }

  ngOnInit() {
    this.reloadTimeout();
  }

  ngOnDestroy() {
    if (this.id) {
      clearInterval(this.id);
      this.id = undefined;
    }
    this.revokeImage(this._displayedObjectUrl);
    this.revokeImage(this.cachedObjectUrl);
  }

  private revokeImage(objUrl?: string) {
    if (objUrl) {
      try {
        URL.revokeObjectURL(objUrl);
      } catch (e) {
        // ignore
      }
    }
  }

  private refreshUrl() {
    this.url.search = `?_ts=${Date.now()}`;
  }

  private reloadPicture() {
    if (document.hidden) return;

    this.refreshUrl();

    this.http
      .get(this.url.toString(), { responseType: 'blob' })
      .subscribe({
        next: (blob: Blob) => {
          const objUrl: string = URL.createObjectURL(blob);
          if (this.cachedObjectUrl && this.cachedObjectUrl !== objUrl) {
            this.revokeImage(this.cachedObjectUrl);
          }
          this.cachedObjectUrl = objUrl;
          // show the cached image
          this.revokeImage(this._displayedObjectUrl);
          this._displayedObjectUrl = this.cachedObjectUrl;
          this._isCameraAvailable = true;
        },
        error: () => {
          // keep last image if available, otherwise clear imageSrc
          this._isCameraAvailable = false;
          if (this.cachedObjectUrl) {
            this.revokeImage(this._displayedObjectUrl);
            this._displayedObjectUrl = this.cachedObjectUrl;
          } else {
            // no previous image: clear displayed url
            this.revokeImage(this._displayedObjectUrl);
            this._displayedObjectUrl = undefined;
          }
        },
      });
  }

  private reloadTimeout() {
    this.reloadPicture();
    this.id = setInterval(
      () => this.reloadPicture(),
      CameraPictureComponent.RELOAD_TIME_MS
    );
  }
}
