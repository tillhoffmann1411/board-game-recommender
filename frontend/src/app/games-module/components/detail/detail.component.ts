import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { IBoardGame, GAMES } from 'src/app/models/game';
import { GameStore } from 'src/app/storemanagement/game.store';

@Component({
  selector: 'app-detail',
  templateUrl: './detail.component.html',
  styleUrls: ['./detail.component.scss']
})
export class DetailComponent implements OnInit {
  onlineGames: IBoardGame[] = GAMES;
  game: IBoardGame;

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

    this.gameStore.getBoardGames.subscribe(games => {
      this.route.queryParams.subscribe(params => {
        this.game = games.find(g => g.id === parseInt(params.id))!;
      });
    });

    this.onlineGames = [...this.onlineGames].splice(0, 2);
    document.querySelector('mat-sidenav-content')!.scrollTop = 0;
  }

  rate(rating: number) {
    this.gameStore.sendRating({ game: this.game.id, rating });
  }

}
