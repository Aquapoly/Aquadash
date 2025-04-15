import { Component, inject, OnInit } from '@angular/core';
import { GlobalSettingsService } from '@app/services/global-settings.service/global-settings.service';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faBell } from '@fortawesome/free-regular-svg-icons';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-navigation-bar',
  standalone: true,
  imports: [FontAwesomeModule, CommonModule],
  templateUrl: './navigation-bar.component.html',
  styleUrl: './navigation-bar.component.scss',
})
export class NavigationBarComponent implements OnInit {
  faBell = faBell;
  darkMode = false;
  private settingsService = inject(GlobalSettingsService);

  notifications = [
    { id: 1, text: "Nouveau message de Jean", read: false },
    { id: 2, text: "Tâche terminée: Dashboard", read: false },
    { id: 3, text: "Mise à jour v1.2 disponible", read: false }
  ];

  forceDropdownOpen = false;

  ngOnInit(): void {
    this.settingsService.applyTheme();
    this.darkMode = this.settingsService.getTheme();
  }

  toggleDarkMode(): void {
    this.settingsService.toggleDarkMode();
    this.darkMode = this.settingsService.getTheme();
  }

  deleteNotification(notificationId:number){
    this.notifications = this.notifications.filter(n => n.id !== notificationId);

    this.forceDropdownOpen = true;
    setTimeout(() => this.forceDropdownOpen = false, 0);

  }

  onNotificationsOpen(){
    this.notifications.forEach(n => {
      n.read = true;
    })
  }

  get unreadCount(): number {
    return this.notifications.filter(n => !n.read).length;
  }

  
}
