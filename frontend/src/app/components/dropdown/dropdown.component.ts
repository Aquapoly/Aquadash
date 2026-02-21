import { Component, Input, Output, EventEmitter, HostListener, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface DropdownOption {
  label: string;
  value: string | number;
}

@Component({
  selector: 'app-dropdown',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dropdown.component.html',
  styleUrls: ['./dropdown.component.css'],
})
export class DropdownComponent {
  @Input() options: DropdownOption[] = [];
  @Input() selectedValue?: string | number;
  @Output() selectionChange = new EventEmitter<DropdownOption>();

  isOpen = false;
  selectedOption?: DropdownOption;

  constructor(private elementRef: ElementRef) {}

  ngOnInit() {
    if (this.selectedValue !== undefined) {
      this.selectedOption = this.options.find((opt) => opt.value === this.selectedValue);
    } else {
      this.selectedOption = this.options.length > 0 ? this.options[0] : undefined;
    }
  }

  ngOnChanges() {
    if (this.selectedValue !== undefined) {
      this.selectedOption = this.options.find((opt) => opt.value === this.selectedValue);
    } else {
      this.selectedOption = this.options.length > 0 ? this.options[0] : undefined;
    }
  }

  toggleDropdown() {
    this.isOpen = !this.isOpen;
  }

  selectOption(option: DropdownOption) {
    this.selectedOption = option;
    this.selectionChange.emit(option);
    this.isOpen = false;
  }

  @HostListener('document:click', ['$event'])
  onClickOutside(event: Event) {
    if (!this.elementRef.nativeElement.contains(event.target)) {
      this.isOpen = false;
    }
  }
}
