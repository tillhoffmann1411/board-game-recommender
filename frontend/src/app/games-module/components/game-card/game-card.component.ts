import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { IBoardGame, IRating } from 'src/app/models/game';
import { GameStore } from 'src/app/storemanagement/game.store';

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
    private gameStore: GameStore,
  ) { }

  ngOnInit(): void {
  }

  rate(rating: number) {
    this.gameStore.sendRating({ gameId: this.game.id, rating });
    this.rated.emit({ gameId: this.game.id, rating } as IRating);
  }

  openDetails() {
    this.router.navigate(['detail'], { relativeTo: this.route.parent, queryParams: { id: this.game.id } })
  }

}
