import { CommonModule } from '@angular/common';
import { Component, ElementRef, Input, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActuatorTypeToName } from '../constants/constants';
import { Actuator } from '@app/interfaces/actuator';

@Component({
  selector: 'app-modify-actuator-modal',
  imports: [CommonModule, FormsModule],
  templateUrl: './modify-actuator-modal.component.html',
  styleUrl: './modify-actuator-modal.component.scss'
})
export class ModifyActuatorModalComponent {

    @ViewChild('modifyActuatorModal') modifyActuatorModal: ElementRef<HTMLDialogElement> | undefined;
    @Input() actuatorName: string;
    @Input() actuatorType: string;
    @Input() modifyActuatorMethod: Function | undefined;

    formInput = {
        name: '',
        type: '',
    };

    constructor() {
      this.actuatorName = '';
      this.actuatorType = '';
    }

    showModal(actuator: Actuator) {
      this.actuatorName = actuator.actuator_name;
      this.actuatorType = actuator.actuator_type;
      const modal = this.modifyActuatorModal?.nativeElement.showModal();
    }

     getNameFromType(type: string) {
      return ActuatorTypeToName[type];
    }

    onTypeChange(event: any) {
      this.formInput.type = event;
      if(this.formInput.type !== '') {
        this.modifyActuatorModal?.nativeElement.querySelector('#submitBtn')?.removeAttribute('disabled');
      }
      else {
        this.modifyActuatorModal?.nativeElement.querySelector('#submitBtn')?.setAttribute('disabled', 'true');
      }
    }

    onSubmit(event: Event) {
      // Validation
      if (!this.formInput['type']) {
        console.error('Form validation failed: No type');
        event.preventDefault();
        return;
      }
      if (!this.formInput['name']) {
        this.formInput['name'] = this.actuatorName;
      }

      console.log(this.formInput)

      const actuator = {
      actuator_type: this.formInput['type'],
      sensor_id: 1, // TODO: ajouter générateur de ID ?
      condition_value: 0,
      activation_condition: 'high',
      activation_period: 0,
      activation_duration: 0,
      last_activated: new Date(),
      enabled: false,
      actuator_name: this.formInput['name']
      };

      if(this.modifyActuatorMethod) this.modifyActuatorMethod(actuator);

      this.onCancel(); // Réinitialiser le formulaire
    }

    onCancel() {
      this.formInput = {
        name: '',
        type: '',
      };
      this.modifyActuatorModal?.nativeElement.close();
    }
}
