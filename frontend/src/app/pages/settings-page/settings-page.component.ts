import { Component, OnInit } from '@angular/core';
import { Actuator } from '../../interfaces/actuator';
import { FormsModule } from '@angular/forms';
import { ViewChild } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { ModalComponent } from '@app/components/modal/modal.component';
import { HttpStatusCode } from '@angular/common/http';
import tippy from 'tippy.js';
import { CommonModule } from '@angular/common';
import { ActuatorTypeToName } from '../../../constants/constants';

@Component({
  selector: 'app-actuator-page',
  templateUrl: './settings-page.component.html',
  styleUrl: './settings-page.component.scss',
  imports: [FormsModule, ModalComponent, CommonModule],
})
export class SettingsPageComponent implements OnInit {
  actuators: Actuator[] = [];
  @ViewChild('responseModal') modal: ModalComponent | undefined;

  constructor(private readonly api: ApiService) {}

  ngOnInit(): void {
    this.api.getActuators(0).subscribe((res) => {
      this.actuators = res.body as Actuator[];
    });
  }
  // Pour bien placer les infobulles
  ngAfterViewInit(): void {
    tippy('[data-tippy-content]', {
      placement: 'bottom',
      animation: 'fade',
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
}
