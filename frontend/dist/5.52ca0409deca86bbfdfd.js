(window.webpackJsonp=window.webpackJsonp||[]).push([[5],{lqJL:function(t,n,e){"use strict";e.r(n),e.d(n,"GamesModuleModule",function(){return $});var i=e("SVse"),a=e("5dmV"),c=e("s7LF"),o=e("iInd"),r=e("8Y7J"),s=e("qGrl"),g=e("o4Yh"),l=e("Tj54");function b(t,n){if(1&t){const t=r.Sb();r.Rb(0,"span",2),r.Rb(1,"mat-icon",3),r.Yb("click",function(){r.lc(t);const e=n.index;return r.cc().rate(e)}),r.uc(2),r.Qb(),r.Qb()}if(2&t){const t=n.$implicit,e=r.cc();r.hc("ngClass",e.rating&&0===e.rating?"neutral":""),r.Bb(2),r.vc(t)}}let m=(()=>{class t{constructor(){this.numStars=5,this.rated=new r.o,this.stars=[]}ngOnInit(){this.rating=this.rating&&this.rating<0?0:this.rating,this.numStars=this.numStars<0?5:this.numStars,this.buildStars()}rate(t){this.rating=t+1,this.buildStars(),this.rated.emit(this.rating)}buildStars(){this.stars=[];for(let t=1;t<=this.numStars;t++)this.stars.push(this.rating&&t<=this.rating?"star":"star_outline")}}return t.\u0275fac=function(n){return new(n||t)},t.\u0275cmp=r.Gb({type:t,selectors:[["app-star-rating"]],inputs:{numStars:"numStars",rating:"rating"},outputs:{rated:"rated"},decls:2,vars:1,consts:[[1,"star-row"],["class","star",3,"ngClass",4,"ngFor","ngForOf"],[1,"star",3,"ngClass"],[3,"click"]],template:function(t,n){1&t&&(r.Rb(0,"div",0),r.tc(1,b,3,2,"span",1),r.Qb()),2&t&&(r.Bb(1),r.hc("ngForOf",n.stars))},directives:[i.j,i.i,l.a],styles:[".star-row[_ngcontent-%COMP%]{display:flex;justify-content:space-evenly}.star[_ngcontent-%COMP%]{cursor:pointer;color:#ff8a1f;display:flex;-webkit-touch-callout:none;-webkit-user-select:none;user-select:none}.neutral[_ngcontent-%COMP%]{color:#000}"]}),t})();function d(t,n){if(1&t){const t=r.Sb();r.Rb(0,"app-star-rating",4),r.Yb("rated",function(n){return r.lc(t),r.cc().rate(n)}),r.Qb()}if(2&t){const t=r.cc();r.hc("numStars",10)("rating",t.rating)}}let p=(()=>{class t{constructor(t,n,e){this.router=t,this.route=n,this.gameStore=e,this.activateDetails=!1,this.deactivateRating=!1,this.rated=new r.o}ngOnInit(){}rate(t){this.gameStore.sendRating({game:this.game.id,rating:t}),this.rated.emit({game:this.game.id,rating:t})}openDetails(){this.router.navigate(["detail"],{relativeTo:this.route.parent,queryParams:{id:this.game.id}})}}return t.\u0275fac=function(n){return new(n||t)(r.Mb(o.c),r.Mb(o.a),r.Mb(s.a))},t.\u0275cmp=r.Gb({type:t,selectors:[["app-game-card"]],inputs:{game:"game",rating:"rating",activateDetails:"activateDetails",deactivateRating:"deactivateRating"},outputs:{rated:"rated"},decls:5,vars:5,consts:[[1,"card"],[3,"src","alt","ngClass","click"],["class","rating",3,"numStars","rating","rated",4,"ngIf"],[1,"name"],[1,"rating",3,"numStars","rating","rated"]],template:function(t,n){1&t&&(r.Rb(0,"div",0),r.Rb(1,"img",1),r.Yb("click",function(){return n.activateDetails&&n.openDetails()}),r.Qb(),r.tc(2,d,1,2,"app-star-rating",2),r.Rb(3,"h2",3),r.uc(4),r.Qb(),r.Qb()),2&t&&(r.Bb(1),r.hc("src",n.game.imageUrl,r.mc)("alt",n.game.name)("ngClass",n.activateDetails?"activatedDetails":""),r.Bb(1),r.hc("ngIf",!n.activateDetails&&!n.deactivateRating),r.Bb(2),r.vc(n.game.name))},directives:[i.i,i.k,m],styles:[".card[_ngcontent-%COMP%]{display:flex;flex-direction:column;margin:1rem .5rem;width:18rem}img[_ngcontent-%COMP%]{width:16rem;height:16rem;margin:0 auto;border-radius:10px;box-shadow:0 0 15px #afafaf}.name[_ngcontent-%COMP%]{text-align:center}.rating[_ngcontent-%COMP%]{margin-top:5px}.activatedDetails[_ngcontent-%COMP%]:hover{transform:scale(.99);box-shadow:0 0 10px #c5c5c5;cursor:pointer}.activatedDetails[_ngcontent-%COMP%]:active{cursor:pointer;transform:scale(.98)}@media only screen and (min-width:768px){.card[_ngcontent-%COMP%]{margin:1rem}}"]}),t})();function u(t,n){if(1&t&&(r.Rb(0,"div"),r.uc(1),r.Qb()),2&t){const t=r.cc(2);r.Bb(1),r.xc("Playtime: ",t.game.minPlaytime," - ",t.game.maxPlaytime,"")}}function h(t,n){if(1&t&&(r.Rb(0,"div"),r.uc(1),r.Qb()),2&t){const t=r.cc(2);r.Bb(1),r.xc("Player: ",t.game.minNumberOfPlayers," - ",t.game.maxNumberOfPlayers,"")}}function f(t,n){if(1&t&&(r.Rb(0,"div"),r.uc(1),r.Qb()),2&t){const t=r.cc(2);r.Bb(1),r.wc("Age: ",t.game.minAge,"+")}}function v(t,n){if(1&t&&(r.Rb(0,"div"),r.uc(1),r.Qb()),2&t){const t=r.cc(2);r.Bb(1),r.wc("Board Game Geek Rating: ",t.game.bggRating,"")}}function R(t,n){if(1&t&&(r.Rb(0,"div"),r.uc(1),r.Qb()),2&t){const t=r.cc(2);r.Bb(1),r.wc("Board Game Geek Average Rating: ",t.game.bggAvgRating,"")}}function O(t,n){if(1&t&&(r.Rb(0,"div"),r.uc(1),r.Qb()),2&t){const t=r.cc(2);r.Bb(1),r.wc("Board Game Atlas Rating: ",t.game.bgaRating,"")}}function C(t,n){if(1&t&&(r.Rb(0,"div"),r.uc(1),r.Qb()),2&t){const t=r.cc(2);r.Bb(1),r.wc("Board Game Atlas Average Rating: ",t.game.bgaAvgRating,"")}}function P(t,n){if(1&t&&(r.Rb(0,"div"),r.Rb(1,"a",10),r.uc(2,"Go to Board Game Atlas"),r.Qb(),r.Qb()),2&t){const t=r.cc(2);r.Bb(1),r.hc("href",t.game.bgaUrl,r.mc)}}function M(t,n){if(1&t&&(r.Rb(0,"div"),r.Rb(1,"a",10),r.uc(2,"Go to the official Website"),r.Qb(),r.Qb()),2&t){const t=r.cc(2);r.Bb(1),r.hc("href",t.game.officialUrl,r.mc)}}function _(t,n){if(1&t&&(r.Rb(0,"section",4),r.Rb(1,"div",5),r.Nb(2,"img",6),r.Qb(),r.Rb(3,"div",7),r.Rb(4,"h1"),r.uc(5),r.Qb(),r.tc(6,u,2,2,"div",8),r.tc(7,h,2,2,"div",8),r.tc(8,f,2,1,"div",8),r.tc(9,v,2,1,"div",8),r.tc(10,R,2,1,"div",8),r.tc(11,O,2,1,"div",8),r.tc(12,C,2,1,"div",8),r.tc(13,P,3,1,"div",8),r.tc(14,M,3,1,"div",8),r.Qb(),r.Nb(15,"div",9),r.Qb()),2&t){const t=r.cc();r.Bb(2),r.hc("src",t.game.imageUrl,r.mc)("alt",t.game.name),r.Bb(3),r.xc("",t.game.name," (",t.game.yearPublished,")"),r.Bb(1),r.hc("ngIf",t.game.minPlaytime),r.Bb(1),r.hc("ngIf",t.game.minNumberOfPlayers),r.Bb(1),r.hc("ngIf",t.game.minAge),r.Bb(1),r.hc("ngIf",t.game.bggRating),r.Bb(1),r.hc("ngIf",t.game.bggAvgRating),r.Bb(1),r.hc("ngIf",t.game.bgaRating),r.Bb(1),r.hc("ngIf",t.game.bgaAvgRating),r.Bb(1),r.hc("ngIf",t.game.bgaUrl&&t.game.bgaUrl.length>5),r.Bb(1),r.hc("ngIf",t.game.officialUrl&&t.game.officialUrl.length>5)}}function w(t,n){if(1&t&&(r.Rb(0,"section",11),r.Rb(1,"h2"),r.uc(2,"Description"),r.Qb(),r.Rb(3,"p",12),r.uc(4),r.Qb(),r.Rb(5,"div",13),r.Rb(6,"mat-expansion-panel",14),r.Rb(7,"mat-expansion-panel-header",15),r.Rb(8,"mat-panel-title"),r.Rb(9,"div"),r.uc(10),r.Qb(),r.Qb(),r.Qb(),r.uc(11),r.Qb(),r.Qb(),r.Qb()),2&t){const t=r.cc();r.Bb(4),r.vc(t.game.description),r.Bb(6),r.vc(t.game.description),r.Bb(1),r.wc(" ",t.game.description," ")}}function Q(t,n){1&t&&r.Nb(0,"app-game-card",19),2&t&&r.hc("game",n.$implicit)("deactivateRating",!0)}function x(t,n){if(1&t&&(r.Rb(0,"section",16),r.Rb(1,"h2"),r.uc(2,"Corresponding online games"),r.Qb(),r.Rb(3,"div",17),r.tc(4,Q,1,2,"app-game-card",18),r.Qb(),r.Qb()),2&t){const t=r.cc();r.Bb(4),r.hc("ngForOf",t.onlineGames)}}let y=(()=>{class t{constructor(t,n,e){this.router=t,this.route=n,this.gameStore=e,this.onlineGames=[],this.rating=0}ngOnInit(){this.gameStore.getRatings.subscribe(t=>{var n;const e=null===(n=t.find(t=>{var n;return t.game===(null===(n=this.game)||void 0===n?void 0:n.id)}))||void 0===n?void 0:n.rating;this.rating=e||0}),this.route.queryParams.subscribe(t=>{t.id&&(this.paramId=t.id,this.gameStore.loadBoardGame(this.paramId))}),this.gameStore.getBoardGames.subscribe(t=>{this.paramId&&(this.game=t.find(t=>t.id==this.paramId))}),this.onlineGames=[...this.onlineGames].splice(0,2),document.querySelector("mat-sidenav-content").scrollTop=0}rate(t){this.gameStore.sendRating({game:this.game.id,rating:t})}goToAmazon(){window.open("https://www.amazon.com/s?k="+this.game.name,"_blank")}}return t.\u0275fac=function(n){return new(n||t)(r.Mb(o.c),r.Mb(o.a),r.Mb(s.a))},t.\u0275cmp=r.Gb({type:t,selectors:[["app-detail"]],decls:4,vars:3,consts:[[1,"wrapper","row"],["class","top-section row",4,"ngIf"],["class","description-section row",4,"ngIf"],["class","game-section row",4,"ngIf"],[1,"top-section","row"],[1,"image","col-3"],[3,"src","alt"],[1,"game-info","col-7"],[4,"ngIf"],[1,"actions","col-2"],[3,"href"],[1,"description-section","row"],[1,"long-description"],[1,"short-description"],[1,"mat-elevation-z0"],["collapsedHeight","80px","expandedHeight","30px"],[1,"game-section","row"],[1,"game-list"],[3,"game","deactivateRating",4,"ngFor","ngForOf"],[3,"game","deactivateRating"]],template:function(t,n){1&t&&(r.Rb(0,"div",0),r.tc(1,_,16,13,"section",1),r.tc(2,w,12,3,"section",2),r.tc(3,x,5,1,"section",3),r.Qb()),2&t&&(r.Bb(1),r.hc("ngIf",n.game),r.Bb(1),r.hc("ngIf",n.game&&n.game.description),r.Bb(1),r.hc("ngIf",n.onlineGames.length>0))},directives:[i.k,g.b,g.c,g.d,i.j,p],styles:[".wrapper[_ngcontent-%COMP%]{margin-top:4rem;padding:0 .25rem}.top-section[_ngcontent-%COMP%]   img[_ngcontent-%COMP%]{width:100%;border-radius:10px}.top-section[_ngcontent-%COMP%]   .game-info[_ngcontent-%COMP%]{padding-left:1rem}.top-section[_ngcontent-%COMP%]   .actions[_ngcontent-%COMP%]{display:flex;justify-content:space-evenly;margin:1rem 0}.top-section[_ngcontent-%COMP%]   .actions[_ngcontent-%COMP%]   mat-icon[_ngcontent-%COMP%]{font-size:3rem}.description-section[_ngcontent-%COMP%]{padding:.5rem;margin:.5rem}.description-section[_ngcontent-%COMP%]   .long-description[_ngcontent-%COMP%]{display:none}.description-section[_ngcontent-%COMP%]   mat-panel-title[_ngcontent-%COMP%]{max-height:53px;text-overflow:ellipsis}.description-section[_ngcontent-%COMP%]   .mat-expanded[_ngcontent-%COMP%]   mat-panel-title[_ngcontent-%COMP%]{display:none}.description-section[_ngcontent-%COMP%]   mat-panel-description[_ngcontent-%COMP%]{display:block}.description-section[_ngcontent-%COMP%]   mat-expansion[_ngcontent-%COMP%]{display:flex;min-width:0}.game-section[_ngcontent-%COMP%]{margin:5rem 0;padding:.5rem;background-color:#d1e3f1;border-radius:10px}.game-section[_ngcontent-%COMP%]   .game-list[_ngcontent-%COMP%]{display:flex;flex-wrap:nowrap;overflow-x:auto}@media only screen and (min-width:768px){.top-section[_ngcontent-%COMP%], .wrapper[_ngcontent-%COMP%]{padding:2rem}.description-section[_ngcontent-%COMP%]{padding:0 3rem}.description-section[_ngcontent-%COMP%]   .short-description[_ngcontent-%COMP%]{display:none}.description-section[_ngcontent-%COMP%]   .long-description[_ngcontent-%COMP%]{display:flex}}"]}),t})();var B=e("JX91"),I=e("lJxs"),S=e("e6WT"),k=e("ZFy/");let G=(()=>{class t{constructor(){this.options={path:"/assets/images/loading-dice.json"}}ngOnInit(){}animationCreated(t){}}return t.\u0275fac=function(n){return new(n||t)},t.\u0275cmp=r.Gb({type:t,selectors:[["app-loading"]],decls:1,vars:0,consts:[[1,"loading-container"]],template:function(t,n){1&t&&r.Nb(0,"div",0)},styles:[".loading-container[_ngcontent-%COMP%]{height:100%;width:100%}"]}),t})();function D(t,n){if(1&t&&(r.Rb(0,"h2"),r.uc(1),r.Qb()),2&t){const t=r.cc(2);r.Bb(1),r.wc("Give\xa0",5-t.ratings.length<0?0:5-t.ratings.length,"\xa0games you like or dislike")}}function F(t,n){if(1&t){const t=r.Sb();r.Rb(0,"section",5),r.tc(1,D,2,1,"h2",3),r.Rb(2,"div",6),r.Rb(3,"label",7),r.uc(4,"Search for games"),r.Qb(),r.Rb(5,"span",8),r.Nb(6,"input",9),r.Rb(7,"div",10),r.Rb(8,"button",11),r.Yb("click",function(){return r.lc(t),r.cc().next()}),r.uc(9," Next "),r.Rb(10,"mat-icon"),r.uc(11,"chevron_right"),r.Qb(),r.Qb(),r.Qb(),r.Qb(),r.Qb(),r.Qb()}if(2&t){const t=r.cc();r.Bb(1),r.hc("ngIf",5-t.ratings.length>0),r.Bb(5),r.hc("formControl",t.searchControl),r.Bb(1),r.hc("matTooltip","Please rate at least"+(5-t.ratings.length)+" more games")("matTooltipDisabled",t.ratings.length>=5),r.Bb(1),r.hc("disabled",t.ratings.length<5)}}function N(t,n){if(1&t&&(r.Rb(0,"div"),r.Nb(1,"app-game-card",13),r.Qb()),2&t){const t=n.$implicit,e=r.cc(2);r.Bb(1),r.hc("game",t)("rating",e.getRatingForGame(t.id))}}function j(t,n){if(1&t&&(r.Pb(0),r.tc(1,N,2,2,"div",12),r.dc(2,"async"),r.Ob()),2&t){const t=r.cc();r.Bb(1),r.hc("ngForOf",r.ec(2,1,t.filteredGames))}}function L(t,n){1&t&&(r.Rb(0,"section",14),r.Rb(1,"h2"),r.uc(2,"Give us a second, we are loading all the greate games."),r.Qb(),r.Nb(3,"app-loading"),r.Qb())}let A=(()=>{class t{constructor(t,n,e){this.router=t,this.route=n,this.gameService=e,this.searchControl=new c.c,this.ratings=[],this.isLoading=!0}ngOnInit(){this.gameService.getRatings.subscribe(t=>this.ratings=t),this.gameService.getBoardGames.subscribe(t=>{t.length>0&&(this.isLoading=!1),this.games=t,this.filteredGames=this.searchControl.valueChanges.pipe(Object(B.a)(""),Object(I.a)(t=>this._filter(t)),Object(I.a)(t=>t.slice(0,15)))})}getRatingForGame(t){var n;return null===(n=this.ratings.find(n=>n.game===t))||void 0===n?void 0:n.rating}next(){this.router.navigate(["recommendations"],{relativeTo:this.route})}_filter(t){const n=this._normalizeValue(t);return this.games.filter(t=>this._normalizeValue(t.name).includes(n))}_normalizeValue(t){return t.toLowerCase().replace(/\s/g,"")}}return t.\u0275fac=function(n){return new(n||t)(r.Mb(o.c),r.Mb(o.a),r.Mb(s.a))},t.\u0275cmp=r.Gb({type:t,selectors:[["app-questionnaire"]],decls:5,vars:3,consts:[[1,"wrapper","row"],["class","search-section row",4,"ngIf"],[1,"game-list","row"],[4,"ngIf"],["class","loading",4,"ngIf"],[1,"search-section","row"],[1,"input-section","col-xl-4"],["for","search"],[1,"input-line"],["matInput","","type","text","autofocus","","placeholder","Search...",1,"search-input",3,"formControl"],[3,"matTooltip","matTooltipDisabled"],[1,"primary",3,"disabled","click"],[4,"ngFor","ngForOf"],[3,"game","rating"],[1,"loading"]],template:function(t,n){1&t&&(r.Rb(0,"div",0),r.tc(1,F,12,5,"section",1),r.Rb(2,"section",2),r.tc(3,j,3,3,"ng-container",3),r.Qb(),r.tc(4,L,4,0,"section",4),r.Qb()),2&t&&(r.Bb(1),r.hc("ngIf",!n.isLoading),r.Bb(2),r.hc("ngIf",!n.isLoading),r.Bb(1),r.hc("ngIf",n.isLoading))},directives:[i.k,S.a,c.a,c.j,c.d,k.a,l.a,i.j,p,G],pipes:[i.b],styles:[".wrapper[_ngcontent-%COMP%]{margin-top:4rem}.search-section[_ngcontent-%COMP%]{display:flex;flex-direction:column;padding:.5rem;margin:.5rem;border-radius:10px;align-items:center}.search-section[_ngcontent-%COMP%]   .input-line[_ngcontent-%COMP%]{display:flex}.search-section[_ngcontent-%COMP%]   .input-line[_ngcontent-%COMP%]   .search-input[_ngcontent-%COMP%]{width:100%;float:left}.search-section[_ngcontent-%COMP%]   .input-line[_ngcontent-%COMP%]   div[_ngcontent-%COMP%]{display:flex}.search-section[_ngcontent-%COMP%]   .input-line[_ngcontent-%COMP%]   div[_ngcontent-%COMP%]   button[_ngcontent-%COMP%]{margin-left:.5rem;float:right}.game-list[_ngcontent-%COMP%]{display:flex;flex-wrap:wrap;justify-content:center}.loading[_ngcontent-%COMP%]{padding:1rem;display:flex;flex-direction:column;align-items:center}@media only screen and (min-width:768px){.search-section[_ngcontent-%COMP%], .wrapper[_ngcontent-%COMP%]{padding:2rem}}"]}),t})();var T=e("ZTz/"),z=e("UhP/"),U=e("Dxy4");function J(t,n){1&t&&r.Nb(0,"app-game-card",29),2&t&&r.hc("game",n.$implicit)("activateDetails",!0)}function q(t,n){if(1&t&&(r.Rb(0,"section",26),r.Rb(1,"div",27),r.tc(2,J,1,2,"app-game-card",28),r.Qb(),r.Qb()),2&t){const t=r.cc();r.Bb(2),r.hc("ngForOf",t.games)}}function Y(t,n){1&t&&(r.Rb(0,"section",30),r.Rb(1,"h2"),r.uc(2,"We are looking for games you will love!"),r.Qb(),r.Nb(3,"app-loading"),r.Qb())}const V=[{path:"recommendations",component:(()=>{class t{constructor(t){this.gameService=t,this.isLoading=!1,this.largeScreen=document.body.clientWidth>768}ngOnInit(){window.addEventListener("resize",t=>{this.largeScreen=document.body.clientWidth>768}),this.isLoading=!0,this.gameService.getRecommendedBoardGames.subscribe(t=>{t.length>0&&(this.isLoading=!1),this.games=t})}}return t.\u0275fac=function(n){return new(n||t)(r.Mb(s.a))},t.\u0275cmp=r.Gb({type:t,selectors:[["app-recommendation"]],decls:66,vars:4,consts:[[1,"wrapper","row"],[1,"filter-section","col-xl-2"],[1,"filter","mat-elevation-z0",3,"expanded","disabled"],[1,"filter"],[1,"filter-actions"],[1,"button","primary"],[1,"input-section"],["for","category"],[1,"input"],["category",""],["value","option1"],["value","option2"],["value","option3"],["for","mechanic"],["mechanic",""],["for","age"],[1,"num-input"],["mat-icon-button","","color","primary"],["type","number","min","0","max","99","value","10",1,"input"],["age",""],["type","number","min","0","max","49","value","2",1,"input"],["type","number","min","1","max","50","value","4",1,"input"],["type","number","min","0","max","999","value","30",1,"input"],["type","number","min","1","max","1000","value","90",1,"input"],["class","game-section col-xl-12",4,"ngIf"],["class","loading",4,"ngIf"],[1,"game-section","col-xl-12"],[1,"game-row"],[3,"game","activateDetails",4,"ngFor","ngForOf"],[3,"game","activateDetails"],[1,"loading"]],template:function(t,n){1&t&&(r.Rb(0,"div",0),r.Rb(1,"section",1),r.Rb(2,"mat-expansion-panel",2),r.Rb(3,"mat-expansion-panel-header"),r.Rb(4,"mat-panel-title"),r.uc(5," Filter "),r.Qb(),r.Qb(),r.Rb(6,"div",3),r.Rb(7,"div",4),r.Rb(8,"button",5),r.Rb(9,"mat-icon"),r.uc(10,"filter_alt"),r.Qb(),r.uc(11," Filter "),r.Qb(),r.Qb(),r.Rb(12,"div",6),r.Rb(13,"label",7),r.uc(14,"Category"),r.Qb(),r.Rb(15,"mat-select",8,9),r.Rb(17,"mat-option",10),r.uc(18,"Option 1"),r.Qb(),r.Rb(19,"mat-option",11),r.uc(20,"Option 2"),r.Qb(),r.Rb(21,"mat-option",12),r.uc(22,"Option 3"),r.Qb(),r.Qb(),r.Qb(),r.Rb(23,"div",6),r.Rb(24,"label",13),r.uc(25,"Game mechanic"),r.Qb(),r.Rb(26,"mat-select",8,14),r.Rb(28,"mat-option",10),r.uc(29,"Option 1"),r.Qb(),r.Rb(30,"mat-option",11),r.uc(31,"Option 2"),r.Qb(),r.Rb(32,"mat-option",12),r.uc(33,"Option 3"),r.Qb(),r.Qb(),r.Qb(),r.Rb(34,"div",6),r.Rb(35,"label",15),r.uc(36,"Min Age"),r.Qb(),r.Rb(37,"div",16),r.Rb(38,"button",17),r.Rb(39,"mat-icon"),r.uc(40,"remove"),r.Qb(),r.Qb(),r.Nb(41,"input",18,19),r.Rb(43,"button",17),r.Rb(44,"mat-icon"),r.uc(45,"add"),r.Qb(),r.Qb(),r.Qb(),r.Qb(),r.Rb(46,"div",6),r.Rb(47,"label",15),r.uc(48,"Player"),r.Qb(),r.Rb(49,"div",16),r.Nb(50,"input",20,19),r.uc(52," \xa0-\xa0 "),r.Nb(53,"input",21,19),r.Qb(),r.Qb(),r.Rb(55,"div",6),r.Rb(56,"label",15),r.uc(57,"Playtime (min)"),r.Qb(),r.Rb(58,"div",16),r.Nb(59,"input",22,19),r.uc(61," \xa0-\xa0 "),r.Nb(62,"input",23,19),r.Qb(),r.Qb(),r.Qb(),r.Qb(),r.Qb(),r.tc(64,q,3,1,"section",24),r.tc(65,Y,4,0,"section",25),r.Qb()),2&t&&(r.Bb(2),r.hc("expanded",n.largeScreen)("disabled",n.isLoading),r.Bb(62),r.hc("ngIf",!n.isLoading),r.Bb(1),r.hc("ngIf",n.isLoading))},directives:[g.b,g.c,g.d,l.a,T.a,z.g,U.a,i.k,i.j,p,G],styles:[".wrapper[_ngcontent-%COMP%]{margin-top:4rem}.mat-expansion-panel[_ngcontent-%COMP%], .mat-expansion-panel-header[_ngcontent-%COMP%]:hover,   .mat-expansion-panel-content>.mat-expansion-panel-body, mat-expansion-panel[_ngcontent-%COMP%]{border-radius:10px;background-color:#d1e3f1}.filter[_ngcontent-%COMP%]{display:none}.filter[_ngcontent-%COMP%]   .num-input[_ngcontent-%COMP%]{display:flex;align-self:center;flex-direction:row;align-items:center;font-weight:500}.filter-actions[_ngcontent-%COMP%]{text-align:center;margin:1rem 0}.game-row[_ngcontent-%COMP%]{display:flex;flex-wrap:wrap;background:#fff}.game-row[_ngcontent-%COMP%]   [_ngcontent-%COMP%]::-webkit-scrollbar{width:0;background:transparent}.game-row[_ngcontent-%COMP%]   [_ngcontent-%COMP%]::-webkit-scrollbar-thumb{background:transparent}.loading[_ngcontent-%COMP%]{padding:1rem;display:flex;flex-direction:column;align-items:center}@media only screen and (min-width:768px){.wrapper[_ngcontent-%COMP%]{padding:1rem}.filter-section[_ngcontent-%COMP%]{padding:1rem 0}.game-section[_ngcontent-%COMP%]{float:right;padding:1rem}.game-section[_ngcontent-%COMP%]   [_ngcontent-%COMP%]::-webkit-scrollbar{width:0;background:transparent;height:.5rem}.game-section[_ngcontent-%COMP%]   [_ngcontent-%COMP%]::-webkit-scrollbar-thumb{background:#d1e3f1;border-radius:10px}.mat-expansion-panel-header[_ngcontent-%COMP%]{display:none}}"]}),t})()},{path:"detail",component:y},{path:"",component:A}];let W=(()=>{class t{}return t.\u0275mod=r.Kb({type:t}),t.\u0275inj=r.Jb({factory:function(n){return new(n||t)},imports:[[o.f.forChild(V)],o.f]}),t})(),$=(()=>{class t{}return t.\u0275mod=r.Kb({type:t}),t.\u0275inj=r.Jb({factory:function(n){return new(n||t)},imports:[[i.c,a.a,W,c.g,c.m]]}),t})()}}]);