import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

@Component({
  selector: 'app-game-card',
  templateUrl: './game-card.component.html',
  styleUrls: ['./game-card.component.scss']
})
export class GameCardComponent implements OnInit {
  @Input() id: number;
  @Input() name: string;
  @Input() description: string;
  @Input() imageUrl?: string;
  @Input() taste: string;

  @Output() rated = new EventEmitter();

  constructor() { }

  ngOnInit(): void {
  }

  like() {
    this.taste = 'like';
    this.rated.emit({ game: this.id, rate: 'like' });
  }

  dislike() {
    this.taste = 'dislike';
    this.rated.emit({ game: this.id, rate: 'dislike' });
  }

}
