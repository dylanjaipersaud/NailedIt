import { Routes } from '@angular/router';
import { Landing } from './landing/landing';
import { PreviewComponent } from './preview/preview';
import { ScheduleComponent } from './schedule/schedule';

export const routes: Routes = [
    { path: '', component: Landing},
    { path: 'preview', component: PreviewComponent},
    { path: 'schedule', component: ScheduleComponent },
    { path: "**", redirectTo: ''}
];