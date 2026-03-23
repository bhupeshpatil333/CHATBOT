import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ChatService } from '../services/chat';

interface ChatMessage {
  text: string;
  sender: 'user' | 'bot';
  showTicketOption?: boolean;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule, MatToolbarModule, MatInputModule, MatButtonModule, MatIconModule, MatTooltipModule],
  templateUrl: './chat.html',
  styleUrls: ['./chat.css']
})
export class ChatComponent implements OnInit {
  activeTab: 'chat' | 'tickets' | 'kb' = 'chat';
  messages: ChatMessage[] = [];
  tickets: any[] = [];
  kbItems: any[] = [];
  filteredKB: any[] = [];
  kbSearchQuery: string = '';
  
  userInput: string = '';
  isTyping: boolean = false;

  quickActions = [
    'VPN not connecting', 'Printer offline', 'Network is slow',
    'ERP login issue', 'Password reset', 'Outlook not syncing'
  ];

  showTicketForm = false;
  ticketIssue = '';
  ticketDesc = '';

  constructor(private chatService: ChatService) {}

  ngOnInit() {
    this.messages.push({ 
      text: `👋 Hello! I'm HelpBot, your Smart IT Helpdesk Assistant.\n\nI can help with:\n• 🌐 Network & VPN issues\n• 🖨️ Printer problems\n• 💼 ERP / SAP / Oracle queries\n• 🔑 Password & account issues\n• 📧 Email & Outlook\n• 💻 Performance & display issues\n\nType your issue below or pick a suggest...`, 
      sender: 'bot' 
    });
  }

  switchTab(tab: 'chat' | 'tickets' | 'kb') {
    this.activeTab = tab;
    if (tab === 'tickets') {
      this.loadTickets();
    } else if (tab === 'kb') {
      this.loadKB();
    }
  }

  loadKB() {
    this.chatService.getKB().subscribe((res: any) => {
      this.kbItems = res;
      this.filteredKB = res;
    });
  }

  filterKB() {
    if (!this.kbSearchQuery) {
      this.filteredKB = this.kbItems;
      return;
    }
    const q = this.kbSearchQuery.toLowerCase();
    this.filteredKB = this.kbItems.filter(i => 
      i.question.toLowerCase().includes(q) || (i.keywords && i.keywords.toLowerCase().includes(q))
    );
  }

  loadTickets() {
    this.chatService.getTickets().subscribe((res: any) => {
      this.tickets = res;
    });
  }

  onQuickAction(action: string) {
    this.userInput = action;
    this.sendMessage();
  }

  sendMessage() {
    if (!this.userInput.trim()) return;

    this.messages.push({ text: this.userInput, sender: 'user' });
    const query = this.userInput;
    this.userInput = '';
    this.isTyping = true;

    this.chatService.sendMessage(query).subscribe({
      next: (res: any) => {
        this.isTyping = false;
        this.messages.push({ 
          text: res.response, 
          sender: 'bot',
          showTicketOption: res.showTicketOption 
        });
      },
      error: () => {
        this.isTyping = false;
        this.messages.push({ text: 'Sorry, server error occurred.', sender: 'bot' });
      }
    });
  }

  openTicketForm() {
    this.showTicketForm = true;
    const lastUserMsg = this.messages.filter(m => m.sender === 'user').pop();
    if (lastUserMsg) {
      this.ticketIssue = lastUserMsg.text;
    }
  }

  submitTicket() {
    this.chatService.createTicket(this.ticketIssue, this.ticketDesc).subscribe((res: any) => {
      this.messages.push({ text: `Ticket Created! Ticket ID is #${res.ticketId}`, sender: 'bot' });
      this.showTicketForm = false;
      this.ticketIssue = '';
      this.ticketDesc = '';
      if (this.activeTab === 'tickets') {
        this.loadTickets();
      }
    });
  }
}
