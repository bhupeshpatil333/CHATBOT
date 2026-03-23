import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  sendMessage(message: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/chatbot/ask`, { message });
  }

  createTicket(issue: string, description: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/ticket`, { issue, description });
  }

  getTickets(): Observable<any> {
    return this.http.get(`${this.apiUrl}/ticket`);
  }

  getKB(): Observable<any> {
    return this.http.get(`${this.apiUrl}/kb`);
  }
}
