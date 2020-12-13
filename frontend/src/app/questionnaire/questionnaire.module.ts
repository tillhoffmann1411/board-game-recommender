import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { MatIconModule } from '@angular/material/icon';
import { QuestionnaireRoutingModule } from './questionnaire-routing.module';
import { QuestionnaireComponent } from './components/questionnaire/questionnaire.component';
import { GenreCardComponent } from './components/genre-card/genre-card.component';


@NgModule({
  declarations: [
    QuestionnaireComponent,
    GenreCardComponent,
  ],
  imports: [
    CommonModule,
    QuestionnaireRoutingModule,
    MatIconModule
  ],
  exports: [
    QuestionnaireComponent,
  ]
})
export class QuestionnaireModule { }
