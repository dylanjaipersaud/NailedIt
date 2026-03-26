import { Component, ElementRef, ViewChild } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-preview',
  templateUrl: './preview.html',
  imports: [RouterLink]
})
export class PreviewComponent {

  @ViewChild('video') videoRef!: ElementRef<HTMLVideoElement>;

  async startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false
      });

      this.videoRef.nativeElement.srcObject = stream;
    } catch (err) {
      console.error('Error accessing camera:', err);
      alert('Camera access denied or not available.');
    }
  }
}