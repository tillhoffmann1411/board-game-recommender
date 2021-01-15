import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { IBoardGame, GAMES } from 'src/app/models/game';

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
    private route: ActivatedRoute
  ) { }

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.game = this.onlineGames.find(g => g.id === parseInt(params.id));
    });
    this.onlineGames = this.onlineGames.splice(0, 2);
  }

  rate(rating: number) {
    // TODO make hier rate update
    this.rating = rating;
  }

}
