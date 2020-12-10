import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-questionnaire',
  templateUrl: './questionnaire.component.html',
  styleUrls: ['./questionnaire.component.scss']
})
export class QuestionnaireComponent implements OnInit {
  genres = [
    {
      text: 'Strategy',
      icon: 'icon-strategy.svg'
    }
  ]

  constructor() { }

  ngOnInit(): void {
  }

}
