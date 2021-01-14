import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../shared-modules/material.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { GamesModuleRoutingModule } from './games-module-routing.module';
import { QuestionnaireComponent } from './components/questionnaire/questionnaire.component';
import { GameCardComponent } from './components/game-card/game-card.component';


@NgModule({
  declarations: [
    QuestionnaireComponent,
    GameCardComponent
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
