import { Component, OnInit, ViewChild } from '@angular/core';
import { Actuator } from '../../interfaces/actuator';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { ModalComponent } from '@app/components/modal/modal.component';
import { NewActuatorModalComponent } from '@app/components/new-actuator-modal/new-actuator-modal.component';
import { HttpStatusCode, HttpClient } from '@angular/common/http';
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
import { Dictionary, error } from 'highcharts';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'app-actuator-page',
  templateUrl: './configuration-page.component.html',
  styleUrl: './configuration-page.component.scss',
  imports: [FormsModule, ModalComponent, CommonModule, NewActuatorModalComponent],
})
export class ConfigurationPageComponent implements OnInit {
  actuators: Actuator[] = [];
  @ViewChild('responseModal') modal: ModalComponent | undefined;
  @ViewChild('newActuatorModal') newActuatorModal: NewActuatorModalComponent | undefined;

  sortColumn: string = '';
  sortDirection: SortDirection = SortDirection.ASC;

  constructor(private readonly api: ApiService) { }

  ngOnInit(): void {
    this.api.getActuators(API_DEFAULTS.ACTUATORS_PAGE).subscribe({
      next: (res) => {
        this.actuators = res.body as Actuator[];
      },
      // e.g. 404 when the prototype does not exist
      error: () => {
        this.actuators = [];
      },
    });
  }

  ngAfterViewInit(): void {
    tippy('[data-tippy-content]', TIPPY_CONFIG);
  }

  protected getNameFromType(type: string): string {
    return ActuatorTypeToName[type] || type;
  }

  onSubmit() {
    forkJoin(
      this.actuators.map((actuator) => this.api.patchActuator(actuator.actuator_id, actuator))
    ).subscribe({
      next: (responses) => {
        if (responses.every((res) => res.status === HttpStatusCode.Ok)) {
          this.showResponseModal(MODAL_MESSAGES.SUCCESS_TITLE, MODAL_MESSAGES.SUCCESS_CONTENT);
        } else {
          this.showResponseModal(MODAL_MESSAGES.ERROR_TITLE, MODAL_MESSAGES.ERROR_CONTENT);
        }
      },
      error: () => this.showResponseModal(MODAL_MESSAGES.ERROR_TITLE, MODAL_MESSAGES.ERROR_CONTENT),
    });
  }

  private showResponseModal(title: string, content: string) {
    if (this.modal) {
      this.modal.title = title;
      this.modal.content = content;
      this.modal.showModal();
    }
  }

  showNewActuatorForm() {    
    if(this.newActuatorModal) {
      this.newActuatorModal.actuatorNumber = this.actuators.length+1;
      this.newActuatorModal.addActuatorMethod = (actuator: Actuator) => this.addActuator(actuator);
    }
    this.newActuatorModal?.showModal();
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

  addActuator(actuatorToAdd: Actuator) {
    // Ajouter à la liste des actuateurs
      this.api.postActuator(actuatorToAdd).subscribe({
        // Any 2xx (201 Created) lands here, 4xx/5xx go to error
        next: () => this.actuators.push(actuatorToAdd),
        error: () => this.showResponseModal(MODAL_MESSAGES.ERROR_TITLE, MODAL_MESSAGES.ERROR_CONTENT_ADDED),
      });
  }

}