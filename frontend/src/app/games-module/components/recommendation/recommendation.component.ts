import { Component, OnInit } from '@angular/core';
import { IBoardGame } from 'src/app/models/game';
import { GameStore } from 'src/app/storemanagement/game.store';

@Component({
  selector: 'app-recommendation',
  templateUrl: './recommendation.component.html',
  styleUrls: ['./recommendation.component.scss']
})
export class RecommendationComponent implements OnInit {
  games: IBoardGame[];
  isLoading = false;
  largeScreen = document.body.clientWidth > 768;

  constructor(
    private gameService: GameStore,
  ) { }

  ngOnInit(): void {
    window.addEventListener('resize', (event) => {
      this.largeScreen = document.body.clientWidth > 768;
    });
    this.isLoading = true;
    this.gameService.getRecommendedBoardGames.subscribe(games => {
      if (games.length > 0) {
        this.isLoading = false;
      }
      this.games = games;
    });
  }

}
