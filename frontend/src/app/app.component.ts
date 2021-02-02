import { Component, OnInit } from '@angular/core';
import { AuthStore } from './storemanagement/auth.store';
import { GameStore } from './storemanagement/game.store';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'board-game-recommender';
  isLoggedIn = false;

  constructor(
    private authService: AuthStore,
    private gameStore: GameStore,
  ) { }

  ngOnInit() {
    this.authService.getIsLoggedIn.subscribe(isloggedIn => {
      this.isLoggedIn = isloggedIn
      if (this.isLoggedIn) {
        this.gameStore.loadBoardGames();
        this.gameStore.loadRatings();
      }
    });

    this.gameStore.getRatings.subscribe(ratings => {
      if (ratings.length >= 5) {
        this.gameStore.loadRecommendedPopularity();
        this.gameStore.loadRecommendedKNN();
        this.gameStore.loadRecommendedItemBased();
        this.gameStore.loadRecommendedCommonBased();
      }
    })
  }
}
