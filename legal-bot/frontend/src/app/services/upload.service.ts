import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent, HttpEventType } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class UploadService {
  private apiUrl = 'http://localhost:8001/api';

  constructor(private http: HttpClient) {}

  uploadFile(file: File, userId: string = 'default_user', offenceNumber?: string): Observable<{ progress: number; docId?: string }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    if (offenceNumber) {
      formData.append('offence_number', offenceNumber);
    }

    return this.http.post(`${this.apiUrl}/artillery/upload`, formData, {
      reportProgress: true,
      observe: 'events'
    }).pipe(
      map((event: HttpEvent<any>) => {
        switch (event.type) {
          case HttpEventType.UploadProgress:
            const progress = event.total ? Math.round(100 * event.loaded / event.total) : 0;
            return { progress };
          case HttpEventType.Response:
            return { progress: 100, docId: event.body?.doc_id };
          default:
            return { progress: 0 };
        }
      })
    );
  }

  uploadImage(file: File, userId: string = 'default_user', offenceNumber?: string): Observable<{ progress: number; docId?: string }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    if (offenceNumber) {
      formData.append('offence_number', offenceNumber);
    }

    return this.http.post(`${this.apiUrl}/artillery/upload`, formData, {
      reportProgress: true,
      observe: 'events'
    }).pipe(
      map((event: HttpEvent<any>) => {
        switch (event.type) {
          case HttpEventType.UploadProgress:
            const progress = event.total ? Math.round(100 * event.loaded / event.total) : 0;
            return { progress };
          case HttpEventType.Response:
            return { progress: 100, docId: event.body?.doc_id };
          default:
            return { progress: 0 };
        }
      })
    );
  }
}