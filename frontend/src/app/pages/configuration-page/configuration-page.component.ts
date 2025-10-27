import { Component, OnInit, ViewChild } from '@angular/core';
import { Actuator } from '../../interfaces/actuator';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { ModalComponent } from '@app/components/modal/modal.component';
import { HttpStatusCode } from '@angular/common/http';
import tippy from 'tippy.js';
import { CommonModule } from '@angular/common';
import {
  ActuatorTypeToName,
  MODAL_MESSAGES,
  API_DEFAULTS,
  TIPPY_CONFIG,
  SortDirection,
} from '../../constants/constants';
import { NONE_TYPE } from '@angular/compiler';

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
  sortDirection: SortDirection = SortDirection.ASC;

  newActuator = {
    actuator_name: '',
    actuator_type: '',
    customType: '',
  };

  constructor(private readonly api: ApiService) {}

  ngOnInit(): void {
    this.api.getActuators(API_DEFAULTS.ACTUATORS_PAGE).subscribe((res) => {
      this.actuators = res.body as Actuator[];
    });
  }

  ngAfterViewInit(): void {
    tippy('[data-tippy-content]', TIPPY_CONFIG);
  }

  protected getNameFromType(type: string): string {
    return ActuatorTypeToName[type] || type;
  }

  onSubmit() {
    this.api.patchActuators(this.actuators).subscribe((res) => {
      if (res.status === HttpStatusCode.Ok) {
        if (this.modal) {
          this.modal.title = MODAL_MESSAGES.SUCCESS_TITLE;
          this.modal.content = MODAL_MESSAGES.SUCCESS_CONTENT;
          this.modal.showModal();
        }
      } else if (this.modal) {
        this.modal.title = MODAL_MESSAGES.ERROR_TITLE;
        this.modal.content = MODAL_MESSAGES.ERROR_CONTENT;
        this.modal.showModal();
      }
    });
  }

  sortTable(column: string): void {
    if (this.sortColumn === column) {
      this.sortDirection =
        this.sortDirection === SortDirection.ASC
          ? SortDirection.DESC
          : SortDirection.ASC;
    } else {
      this.sortColumn = column;
      this.sortDirection = SortDirection.ASC;
    }

    this.actuators.sort((a, b) => {
      const [valueA, valueB] = [
        a[column as keyof Actuator],
        b[column as keyof Actuator],
      ];
      return (
        (valueA > valueB ? 1 : -1) *
        (this.sortDirection === SortDirection.ASC ? 1 : -1)
      );
    });
  }

  addActuator(): void {
    // Validation
    if (!this.newActuator.actuator_type) {
      console.error('Form validation failed');
      return;
    }

    if (!this.newActuator.actuator_name) {
      this.newActuator.actuator_name = 'Actuateur #'+(this.actuators.length + 1)
    }

    const actuatorType = this.newActuator.actuator_type === 'Autre' 
      ? this.newActuator.customType 
      : this.newActuator.actuator_type;

    const actuator = {
      actuator_id : 0, // TODO ajouter générateur de ID
      actuator_name: this.newActuator.actuator_name,
      actuator_type: actuatorType,
      condition_value: 0,
      enabled: false,
      activation_condition: 'high',
      activation_period: 0,
      activation_duration: 0,
      last_activated: new Date()
    };

    // Ajouter à la liste des actuateurs
    this.actuators.push(actuator);
    
    // TODO : ajouter au backend

    // Reset form
    this.resetForm();
  }

  resetForm(): void {
    this.newActuator = {
      actuator_name: '',
      actuator_type: '',
      customType: '',
    };
  }

}
