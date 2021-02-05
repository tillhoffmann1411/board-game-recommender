import { Component, EventEmitter, Input, OnChanges, OnInit, Output } from '@angular/core';

@Component({
  selector: 'app-star-rating',
  templateUrl: './star-rating.component.html',
  styleUrls: ['./star-rating.component.scss']
})
export class StarRatingComponent implements OnInit, OnChanges {
  @Input() numStars: number = 5;
  @Input() rating: number | undefined;

  @Output() rated = new EventEmitter();

  stars: string[] = [];

  constructor() { }

  ngOnInit(): void {
    this._rebuild();
  }

  ngOnChanges() {
    this._rebuild();
  }


  rate(starIndex: number) {
    this.rating = starIndex + 1;
    this.buildStars();
    this.rated.emit(this.rating);
  }

  buildStars() {
    this.stars = [];
    for (let i = 1; i <= this.numStars; i++) {
      const star = this.rating && i <= this.rating ? 'star' : 'star_outline';
      this.stars.push(star);
    }
  }

  private _rebuild() {
    this.rating = this.rating && this.rating <= 0 ? 0 : this.rating;
    this.numStars = this.numStars < 0 ? 5 : this.numStars;
    this.buildStars();
  }
}
