import { core } from '@angular/compiler';
import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-genre-card',
  templateUrl: './genre-card.component.html',
  styleUrls: ['./genre-card.component.scss']
})
export class GenreCardComponent implements OnInit {
  @Input() icon: string;
  @Input() text: string;

  constructor(
  ) { }

  ngOnInit(): void {

  }

}


// src="../../../../assets/icons/{{ icon }}"