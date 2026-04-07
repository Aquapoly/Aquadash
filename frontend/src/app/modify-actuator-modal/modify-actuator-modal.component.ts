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
    @Input() modifyActuatorMethod: Function | undefined;
    
    actuator: Actuator | undefined;

    formInput = {
      name: '',
      type: '',
    };

    showModal(actuator: Actuator) {
      this.actuator = actuator;

      this.actuator.actuator_name = actuator.actuator_name ? actuator.actuator_name : "{name_not_saved}";
      this.actuator.actuator_type = actuator.actuator_type;

      this.formInput.name = this.actuator.actuator_name;
      this.formInput.type = this.actuator.actuator_type;

      const modal = this.modifyActuatorModal?.nativeElement.showModal();
    }

    getNameFromType(type: string) {
      return ActuatorTypeToName[type];
    }

    getActuatorName() {
      return this.actuator?.actuator_name;
    }

    onTypeChange(newType: string) {
      this.formInput.type = newType;
    }

    onSubmit(event: Event) {
      if(this.actuator) {
        // Validation
        if (!this.formInput['type']) {
          this.formInput['type'] = this.actuator.actuator_type;
        }
        if (!this.formInput['name']) {
          this.formInput['name'] = this.actuator.actuator_name;
        }

        this.actuator.actuator_name = this.formInput['name'];
        this.actuator.actuator_type = this.formInput['type'];
      }

      if(this.modifyActuatorMethod) this.modifyActuatorMethod(this.actuator);

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
