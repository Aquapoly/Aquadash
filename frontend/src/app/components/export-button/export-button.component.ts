import { Component } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

@Component({
  selector: 'app-export-button',
  imports: [FontAwesomeModule],
  templateUrl: './export-button.component.html',
  styleUrl: './export-button.component.scss',
})
export class ExportButtonComponent {
  onClick() {
    console.log("ca exporte");
  }
}
