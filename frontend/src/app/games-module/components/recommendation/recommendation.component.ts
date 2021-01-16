import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { IBoardGame, GAMES } from 'src/app/models/game';
import { GameStore } from 'src/app/storemanagement/game.store';

@Component({
  selector: 'app-recommendation',
  templateUrl: './recommendation.component.html',
  styleUrls: ['./recommendation.component.scss']
})
export class RecommendationComponent implements OnInit {
  games: Observable<IBoardGame[]>;

  constructor(
    private gameService: GameStore,
  ) { }

  ngOnInit(): void {
    this.gameService.loadRecommendedBoardGames();

    this.games = this.gameService.getRecommendedBoardGames;
  }

}
