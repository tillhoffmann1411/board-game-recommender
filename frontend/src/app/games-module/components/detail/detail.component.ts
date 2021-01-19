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
  game: IBoardGame | undefined;

  rating = 0;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private gameStore: GameStore,
  ) { }

  ngOnInit(): void {
    window.scrollTo(0, 0);
    this.route.queryParams.subscribe(params => {
      this.game = this.onlineGames.find(g => g.id === parseInt(params.id));
    });

    this.gameStore.getRatings.subscribe(ratings => {
      const userRate = ratings.find(rating => rating.gameId === this.game?.id)?.rating;
      this.rating = userRate ? userRate : 0;
    });

    this.onlineGames = [...this.onlineGames].splice(0, 2);
  }

  rate(rating: number) {
    // TODO make hier rate update
    this.rating = rating;
  }

}
