import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { QuestionnaireRoutingModule } from './questionnaire-routing.module';
import { QuestionnaireComponent } from './components/questionnaire/questionnaire.component';
import { GenreCardComponent } from './components/genre-card/genre-card.component';


@NgModule({
  declarations: [QuestionnaireComponent, GenreCardComponent],
  imports: [
    CommonModule,
    QuestionnaireRoutingModule
  ]
})
export class QuestionnaireModule { }
