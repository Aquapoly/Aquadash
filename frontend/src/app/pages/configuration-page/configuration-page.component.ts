import { Component, OnInit, ViewChild } from '@angular/core';
import { Actuator } from '../../interfaces/actuator';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { ModalComponent } from '@app/components/modal/modal.component';
import { HttpStatusCode } from '@angular/common/http';
import tippy from 'tippy.js';
import 'tippy.js/themes/light.css';
import { CommonModule } from '@angular/common';
import { ActuatorTypeToName } from '../../../constants/constants';

@Component({
  selector: 'app-actuator-page',
  templateUrl: './configuration-page.component.html',
  styleUrl: './configuration-page.component.scss',
  imports: [FormsModule, ModalComponent, CommonModule],
})
export class ConfigurationPageComponent implements OnInit {
  actuators: Actuator[] = [];
  @ViewChild('responseModal') modal: ModalComponent | undefined;

  sortColumn: string = '';
  sortDirection: 'asc' | 'desc' = 'asc';

  constructor(private readonly api: ApiService) {}

  ngOnInit(): void {
    this.api.getActuators(0).subscribe((res) => {
      this.actuators = res.body as Actuator[];
    });
  }
  // Pour bien placer les infobulles
  ngAfterViewInit(): void {
    tippy('[data-tippy-content]', {
      placement: 'top',
      animation: 'scale-subtle',
      theme: 'light',
      arrow: true,
    });
  }

  protected getNameFromType(type: string): string {
    return ActuatorTypeToName[type] || type;
  }

  onSubmit() {
    this.api.patchActuators(this.actuators).subscribe((res) => {
      if (res.status === HttpStatusCode.Ok) {
        if (this.modal) {
          this.modal.title = 'Succès';
          this.modal.content = 'Les paramètres ont été mis à jour avec succès';
          this.modal.showModal();
        }
      } else if (this.modal) {
        this.modal.title = 'Erreur';
        this.modal.content =
          'Une erreur est survenue lors de la mise à jour des paramètres';
        this.modal.showModal();
      }
    });
  }

  sortTable(column: string): void {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }

    this.actuators.sort((a, b) => {
      const [valueA, valueB] = [
        a[column as keyof Actuator],
        b[column as keyof Actuator],
      ];
      return (
        (valueA > valueB ? 1 : -1) * (this.sortDirection === 'asc' ? 1 : -1)
      );
    });
  }
}
