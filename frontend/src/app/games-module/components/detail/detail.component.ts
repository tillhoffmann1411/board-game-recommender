import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { IBoardGame } from 'src/app/models/game';
import { GameStore } from 'src/app/storemanagement/game.store';

@Component({
  selector: 'app-detail',
  templateUrl: './detail.component.html',
  styleUrls: ['./detail.component.scss']
})
export class DetailComponent implements OnInit {
  onlineGames: IBoardGame[] = [];
  game: IBoardGame;
  paramId: number;

  rating = 0;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private gameStore: GameStore,
  ) { }

  ngOnInit(): void {
    this.gameStore.getRatings.subscribe(ratings => {
      const userRate = ratings.find(rating => rating.game === this.game?.id)?.rating;
      this.rating = userRate ? userRate : 0;
    });


    this.route.queryParams.subscribe(params => {
      if (params.id) {
        this.paramId = params.id
        this.gameStore.loadBoardGame(this.paramId);
      }
    });
    this.gameStore.getBoardGames.subscribe(games => {
      if (this.paramId) {
        this.game = games.find(g => {
          return g.id == this.paramId;
        })!;
      }
    });

    this.onlineGames = [...this.onlineGames].splice(0, 2);
    document.querySelector('mat-sidenav-content')!.scrollTop = 0;
  }

  rate(rating: number) {
    this.gameStore.sendRating({ game: this.game.id, rating });
  }

  goToAmazon() {
    window.open('https://www.amazon.com/s?k=' + this.game.name, '_blank');
  }

}
