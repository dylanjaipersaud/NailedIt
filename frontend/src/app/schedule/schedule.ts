import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-schedule',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './schedule.html',
})

export class ScheduleComponent {

  currentDate = new Date();
  selectedDate: Date | null = null;
  selectedTime: string = '';

  days: Date[] = [];

  // Form fields
  firstName = '';
  lastName = '';
  email = '';
  phone = '';

  // Example time slots
  timeSlots: string[] = [
    '10:00 AM',
    '11:00 AM',
    '12:00 PM',
    '1:00 PM',
    '2:00 PM',
    '3:00 PM',
    '4:00 PM'
  ];

  ngOnInit() {
    this.generateCalendar();
  }

  generateCalendar() {
    this.days = [];

    const year = this.currentDate.getFullYear();
    const month = this.currentDate.getMonth();

    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);

    const startDay = firstDay.getDay();

    for (let i = 0; i < startDay; i++) {
      this.days.push(new Date(0));
    }

    for (let i = 1; i <= lastDay.getDate(); i++) {
      this.days.push(new Date(year, month, i));
    }
  }

  changeMonth(offset: number) {
    this.currentDate.setMonth(this.currentDate.getMonth() + offset);
    this.generateCalendar();
  }

  selectDate(day: Date) {
    if (day.getTime() === 0) return;

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (day < today) return;

    this.selectedDate = day;
    this.selectedTime = ''; // reset time when new date selected
  }

  selectTime(time: string) {
    this.selectedTime = time;
  }

  isSameDay(d1: Date | null, d2: Date) {
    return d1 &&
      d1.getDate() === d2.getDate() &&
      d1.getMonth() === d2.getMonth() &&
      d1.getFullYear() === d2.getFullYear();
  }

  isToday(day: Date) {
    const today = new Date();
    return this.isSameDay(today, day);
  }

  isPast(day: Date) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return day < today;
  }

  formatMonth() {
    return this.currentDate.toLocaleString('default', {
      month: 'long',
      year: 'numeric'
    });
  }

  bookAppointment() {
    if (!this.selectedDate || !this.selectedTime || !this.firstName || !this.email) {
      alert('Please complete all required fields.');
      return;
    }

    alert(`Booked ${this.selectedDate} at ${this.selectedTime}`);
  }
}