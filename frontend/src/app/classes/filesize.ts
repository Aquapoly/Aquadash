import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'filesize'
})
export class FileSizePipe implements PipeTransform {
  transform(nBytes: number): string {
    const BASE: number = 1024;
    if (nBytes < BASE) return `${nBytes} B`;
    nBytes /= BASE;
    if (nBytes < BASE) return `${nBytes.toFixed(2)} KiB`;
    nBytes /= BASE;
    if (nBytes < BASE) return `${nBytes.toFixed(2)} MiB`;
    nBytes /= BASE;
    return `${nBytes.toFixed(2)} GiB`;
  }
}
