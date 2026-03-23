import { Component, OnInit, ViewChild } from '@angular/core';
import { Actuator } from '../../interfaces/actuator';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { ModalComponent } from '@app/components/modal/modal.component';
import { NewActuatorModalComponent } from '@app/components/new-actuator-modal/new-actuator-modal.component';
import { ModifyActuatorModalComponent } from '@app/modify-actuator-modal/modify-actuator-modal.component';
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

@Component({
  selector: 'app-actuator-page',
  templateUrl: './configuration-page.component.html',
  styleUrl: './configuration-page.component.scss',
  imports: [FormsModule, ModalComponent, CommonModule, NewActuatorModalComponent, ModifyActuatorModalComponent],
})
export class ConfigurationPageComponent implements OnInit {
  actuators: Actuator[] = [];
  @ViewChild('responseModal') modal: ModalComponent | undefined;
  @ViewChild('newActuatorModal') newActuatorModal: NewActuatorModalComponent | undefined;
  @ViewChild('modifyActuatorModal') modifyActuatorModal : ModifyActuatorModalComponent | undefined;

  sortColumn: string = '';
  sortDirection: SortDirection = SortDirection.ASC;

  constructor(private readonly api: ApiService) { }

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

  showNewActuatorForm() {   
    if(this.newActuatorModal) {
      this.newActuatorModal.actuatorNumber = this.actuators.length+1;
      this.newActuatorModal.addActuatorMethod = (actuator: Actuator) => this.addActuator(actuator);
    }
    this.newActuatorModal?.showModal();
  }

  showModifyActuatorForm(actuator: Actuator) {
    if(this.modifyActuatorModal) {
      this.modifyActuatorModal.actuatorName = actuator.actuator_name; // TODO: not saved in database!
      this.modifyActuatorModal.actuatorType = actuator.actuator_type;
      this.modifyActuatorModal.modifyActuatorMethod = (actuator: Actuator) => this.modifyActuator(actuator);
    }
    this.modifyActuatorModal?.showModal(actuator);
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
    // Add to actuator list
      this.api.postActuator(actuatorToAdd).subscribe((res)=>{
        if(res.status === HttpStatusCode.Ok) {
          this.actuators.push(actuatorToAdd);
        }
        else if (this.modal) {
          this.modal.title = MODAL_MESSAGES.ERROR_TITLE;
          this.modal.content = MODAL_MESSAGES.ERROR_CONTENT_ADDED;
          this.modal.showModal();
        }
      });
  }

  modifyActuator(actuatorToModify: Actuator) {
    // TODO:
  }

}