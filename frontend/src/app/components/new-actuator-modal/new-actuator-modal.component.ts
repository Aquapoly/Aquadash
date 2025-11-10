import { CommonModule } from '@angular/common';
import { Component, ElementRef, Input, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Actuator } from '@app/interfaces/actuator';

@Component({
  selector: 'app-new-actuator-modal',
  imports: [CommonModule, FormsModule],
  templateUrl: './new-actuator-modal.component.html',
  styleUrl: './new-actuator-modal.component.scss'
})
export class NewActuatorModalComponent {
    @ViewChild('newActuatorModal') newActuatorModal: ElementRef<HTMLDialogElement> | undefined;
    @Input() actuatorNumber: number | undefined;
    @Input() addActuatorMethod: Function | undefined;

    formInput = {
        name: '',
        type: '',
      };

    showModal() {
      const modal = this.newActuatorModal?.nativeElement.showModal();
      
    }
    onSubmit(event: Event) {
      // Validation
      if (!this.formInput['type']) {
        console.error('Form validation failed: No type');
        event.preventDefault();
        return;
      }
      if (!this.formInput['name']) {
        if(!this.actuatorNumber) this.actuatorNumber = 1
        this.formInput['name'] = 'Actuateur #'+this.actuatorNumber
      }

      console.log(this.formInput)

      const actuator = {
      actuator_type: this.formInput['type'],
      sensor_id: 1, // TODO ajouter générateur de ID ?
      condition_value: 0,
      activation_condition: 'high',
      activation_period: 0,
      activation_duration: 0,
      last_activated: new Date(),
      enabled: false,
      actuator_name: this.formInput['name']
      };

      // POST format
    // {
    //   "actuator_type": "acid_pump",
    //   "sensor_id": 0,
    //   "condition_value": 0,
    //   "activation_condition": "high",
    //   "activation_period": 0,
    //   "activation_duration": 0
    // }

      if(this.addActuatorMethod) this.addActuatorMethod(actuator);
    }
}
