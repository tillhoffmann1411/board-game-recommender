import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { IBoardGame } from 'src/app/models/game';

@Component({
  selector: 'app-game-card',
  templateUrl: './game-card.component.html',
  styleUrls: ['./game-card.component.scss']
})
export class GameCardComponent implements OnInit {
  @Input() game: IBoardGame;
  @Input() taste: string = 'neutral';
  @Input() activateDetails = false;
  @Input() deactivateRating = false;

  @Output() rated = new EventEmitter();

  constructor(
    private router: Router,
    private route: ActivatedRoute,
  ) { }

  ngOnInit(): void {
  }

  rate(rating: number) {
    // TODO make hier rate update
    this.rated.emit({ gameId: this.game.id, rating });
  }

  openDetails() {
    console.log('id', this.game.id);
    this.router.navigate(['detail'], { relativeTo: this.route.parent, queryParams: { id: this.game.id } })
  }

}
