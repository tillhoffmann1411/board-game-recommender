import { Component, OnInit } from '@angular/core';
import { IBoardGame, IRecResponse } from 'src/app/models/game';
import { GameStore } from 'src/app/storemanagement/game.store';

@Component({
  selector: 'app-recommendation',
  templateUrl: './recommendation.component.html',
  styleUrls: ['./recommendation.component.scss']
})
export class RecommendationComponent implements OnInit {
  commonBased: IBoardGame[] = [];
  knn: IBoardGame[] = [];
  itemBased: IBoardGame[] = [];

  gameMap: Map<number, IBoardGame> = new Map();

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
    this.gameService.getBoardGames.subscribe(games => {
      this.gameService.getRecommendedBoardGames.subscribe(recommendations => {
        if (games.length > 0 &&
          (recommendations.commonBased.length > 0 ||
            recommendations.knn.length > 0 ||
            recommendations.itemBased.length > 0)) {
          this.isLoading = false;
        }
        games.forEach(g => this.gameMap.set(g.id, g));

        this.commonBased = this.getGameListFromKeys(recommendations.commonBased, this.gameMap);
        this.knn = this.getGameListFromKeys(recommendations.knn, this.gameMap);
        this.itemBased = this.getGameListFromKeys(recommendations.itemBased, this.gameMap);
      });
    });
  }

  getGameListFromKeys(recommendations: IRecResponse[], games: Map<number, IBoardGame>) {
    const newList: IBoardGame[] = [];
    if (recommendations.length > 0) {
      for (let i = 0; i < 50; i++) {
        if (recommendations[i]) {
          const game = games.get(recommendations[i].gameKey);
          if (game) {
            newList.push(game);
          }
          continue;
        } else {
          break;
        }
      }
    }
    return newList;
  }

}