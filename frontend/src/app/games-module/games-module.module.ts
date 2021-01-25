import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../shared/material.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { GamesModuleRoutingModule } from './games-module-routing.module';
import { QuestionnaireComponent } from './components/questionnaire/questionnaire.component';
import { GameCardComponent } from './components/game-card/game-card.component';
import { RecommendationComponent } from './components/recommendation/recommendation.component';
import { DetailComponent } from './components/detail/detail.component';



@NgModule({
  declarations: [
    QuestionnaireComponent,
    GameCardComponent,
    RecommendationComponent,
    DetailComponent
  ],
  imports: [
    CommonModule,
    MaterialModule,
    GamesModuleRoutingModule,
    FormsModule,
    ReactiveFormsModule,
  ]
})
export class GamesModuleModule { }
