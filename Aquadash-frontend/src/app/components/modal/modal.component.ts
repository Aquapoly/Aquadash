import { Component, ElementRef, Input, ViewChild } from '@angular/core';

@Component({
    selector: 'app-modal',
    imports: [],
    templateUrl: './modal.component.html',
    styleUrl: './modal.component.scss'
})
export class ModalComponent {
  @Input() title: string = '';
  @Input() content: string = '';
  @ViewChild('modal') modal: ElementRef<HTMLDialogElement> | undefined;

  showModal() {
    const modal = this.modal?.nativeElement.showModal();
  }
}
