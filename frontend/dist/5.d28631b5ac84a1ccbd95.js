(window.webpackJsonp=window.webpackJsonp||[]).push([[5],{lqJL:function(n,t,e){"use strict";e.r(t),e.d(t,"GamesModuleModule",function(){return bn});var i=e("SVse"),a=e("5dmV"),o=e("s7LF"),c=e("iInd"),s=e("8Y7J"),r=e("qGrl"),g=e("Tj54");function m(n,t){if(1&n){const n=s.Sb();s.Rb(0,"span",2),s.Rb(1,"mat-icon",3),s.Yb("click",function(){s.mc(n);const e=t.index;return s.cc().rate(e)}),s.vc(2),s.Qb(),s.Qb()}if(2&n){const n=t.$implicit,e=s.cc();s.hc("ngClass",0===e.rating?"neutral":""),s.Bb(2),s.wc(n)}}let l=(()=>{class n{constructor(){this.numStars=5,this.rated=new s.o,this.stars=[]}ngOnInit(){this._rebuild()}ngOnChanges(){this._rebuild()}rate(n){this.rating=n+1,this.buildStars(),this.rated.emit(this.rating)}buildStars(){this.stars=[];for(let n=1;n<=this.numStars;n++)this.stars.push(this.rating&&n<=this.rating?"star":"star_outline")}_rebuild(){this.rating=this.rating&&this.rating<=0?0:this.rating,this.numStars=this.numStars<0?5:this.numStars,this.buildStars()}}return n.\u0275fac=function(t){return new(t||n)},n.\u0275cmp=s.Gb({type:n,selectors:[["app-star-rating"]],inputs:{numStars:"numStars",rating:"rating"},outputs:{rated:"rated"},features:[s.zb],decls:2,vars:1,consts:[[1,"star-row"],["class","star",3,"ngClass",4,"ngFor","ngForOf"],[1,"star",3,"ngClass"],[3,"click"]],template:function(n,t){1&n&&(s.Rb(0,"div",0),s.uc(1,m,3,2,"span",1),s.Qb()),2&n&&(s.Bb(1),s.hc("ngForOf",t.stars))},directives:[i.j,i.i,g.a],styles:[".star-row[_ngcontent-%COMP%]{display:flex;justify-content:space-evenly}.star[_ngcontent-%COMP%]{cursor:pointer;color:#ff8a1f;display:flex;-webkit-touch-callout:none;-webkit-user-select:none;user-select:none}.neutral[_ngcontent-%COMP%]{color:#000}"]}),n})();var b=e("ZFy/"),d=e("DPnb");let h=(()=>{class n{constructor(){this.options={path:"/assets/images/loading-dice.json"}}ngOnInit(){}animationCreated(n){}}return n.\u0275fac=function(t){return new(t||n)},n.\u0275cmp=s.Gb({type:n,selectors:[["app-loading"]],decls:2,vars:1,consts:[[1,"loading-container"],[3,"options","animationCreated"]],template:function(n,t){1&n&&(s.Rb(0,"div",0),s.Rb(1,"ng-lottie",1),s.Yb("animationCreated",function(n){return t.animationCreated(n)}),s.Qb(),s.Qb()),2&n&&(s.Bb(1),s.hc("options",t.options))},directives:[d.a],styles:[".loading-container[_ngcontent-%COMP%]{height:100%;width:100%}"]}),n})();function u(n,t){if(1&n&&(s.Rb(0,"span"),s.vc(1),s.Qb()),2&n){const n=s.cc(2);s.Bb(1),s.xc("(",n.game.yearPublished,")")}}const p=function(n){return{link:n}};function f(n,t){if(1&n){const n=s.Sb();s.Rb(0,"div",18),s.Yb("click",function(){s.mc(n);const e=t.$implicit;return s.cc(2).clickOnInfo(e)}),s.Rb(1,"mat-icon"),s.vc(2),s.Qb(),s.Rb(3,"div",19),s.vc(4),s.Qb(),s.Qb()}if(2&n){const n=t.$implicit;s.hc("matTooltip",n.description||"")("ngClass",s.ic(4,p,n.link)),s.Bb(2),s.wc(n.icon),s.Bb(2),s.wc(n.text)}}function O(n,t){if(1&n){const n=s.Sb();s.Rb(0,"div",24),s.Yb("click",function(){s.mc(n);const e=t.$implicit;return s.cc(3).clickOnInfo(e)}),s.Rb(1,"mat-icon"),s.vc(2),s.Qb(),s.Rb(3,"span"),s.vc(4),s.Qb(),s.Qb()}if(2&n){const n=t.$implicit;s.hc("ngClass",s.ic(3,p,n.link)),s.Bb(2),s.wc(n.icon),s.Bb(2),s.wc(n.text)}}function M(n,t){if(1&n&&(s.Rb(0,"div",20),s.Rb(1,"div",21),s.Nb(2,"img",22),s.Rb(3,"span",19),s.vc(4," Board Game Atlas "),s.Qb(),s.Qb(),s.uc(5,O,5,5,"div",23),s.Qb()),2&n){const n=s.cc(2);s.Bb(5),s.hc("ngForOf",n.bgaInfos)}}function v(n,t){if(1&n){const n=s.Sb();s.Rb(0,"div",24),s.Yb("click",function(){s.mc(n);const e=t.$implicit;return s.cc(3).clickOnInfo(e)}),s.Rb(1,"mat-icon"),s.vc(2),s.Qb(),s.Rb(3,"span"),s.vc(4),s.Qb(),s.Qb()}if(2&n){const n=t.$implicit;s.hc("ngClass",s.ic(3,p,n.link)),s.Bb(2),s.wc(n.icon),s.Bb(2),s.wc(n.text)}}function P(n,t){if(1&n&&(s.Rb(0,"div",20),s.Rb(1,"div",21),s.Nb(2,"img",25),s.Rb(3,"span",19),s.vc(4," Board Game Geek "),s.Qb(),s.Qb(),s.uc(5,v,5,5,"div",23),s.Qb()),2&n){const n=s.cc(2);s.Bb(5),s.hc("ngForOf",n.bggInfos)}}function C(n,t){if(1&n){const n=s.Sb();s.Rb(0,"div",27),s.Yb("click",function(){s.mc(n);const e=t.$implicit;return s.cc(3).clickOnOnlinegame(e)}),s.Nb(1,"img",28),s.Rb(2,"span"),s.vc(3),s.Qb(),s.Qb()}if(2&n){const n=t.$implicit,e=s.cc(3);s.Bb(1),s.hc("src",e.getOnlineGameIcon(n.origin),s.nc),s.Bb(2),s.yc("Play ",n.name," on ",n.origin,"")}}function R(n,t){if(1&n&&(s.Rb(0,"div",20),s.Rb(1,"div",21),s.Rb(2,"div",19),s.vc(3," Play this game online! "),s.Qb(),s.Qb(),s.uc(4,C,4,3,"div",26),s.Qb()),2&n){const n=s.cc(2);s.Bb(4),s.hc("ngForOf",n.game.onlineGames)}}function _(n,t){if(1&n){const n=s.Sb();s.Rb(0,"section",5),s.Rb(1,"div",6),s.Nb(2,"img",7),s.Qb(),s.Rb(3,"div",8),s.Rb(4,"h1"),s.vc(5),s.uc(6,u,2,1,"span",9),s.Qb(),s.Rb(7,"div",10),s.uc(8,f,5,6,"div",11),s.Qb(),s.uc(9,M,6,1,"div",12),s.uc(10,P,6,1,"div",12),s.uc(11,R,5,1,"div",12),s.Qb(),s.Rb(12,"div",13),s.Rb(13,"app-star-rating",14),s.Yb("rated",function(t){return s.mc(n),s.cc().rate(t)}),s.Qb(),s.Rb(14,"div",15),s.Rb(15,"button",16),s.Yb("click",function(){return s.mc(n),s.cc().removeRating()}),s.vc(16,"Remove Rating"),s.Qb(),s.Rb(17,"button",17),s.Yb("click",function(){return s.mc(n),s.cc().goToAmazon()}),s.vc(18,"Amazon"),s.Qb(),s.Qb(),s.Qb(),s.Qb()}if(2&n){const n=s.cc();s.Bb(2),s.hc("src",n.game.imageUrl,s.nc)("alt",n.game.name),s.Bb(3),s.xc("",n.game.name," "),s.Bb(1),s.hc("ngIf",n.game.yearPublished&&n.game.yearPublished>0),s.Bb(2),s.hc("ngForOf",n.gameInfos),s.Bb(1),s.hc("ngIf",n.bgaInfos.length>0),s.Bb(1),s.hc("ngIf",n.bggInfos.length>0),s.Bb(1),s.hc("ngIf",n.game&&n.game.onlineGames&&n.game.onlineGames.length>0),s.Bb(2),s.hc("numStars",10)("rating",n.rating),s.Bb(2),s.hc("disabled",!n.userRate)}}function w(n,t){1&n&&s.Nb(0,"img",37),2&n&&s.hc("src",t.$implicit.imageUrl,s.nc)}function x(n,t){if(1&n&&(s.Rb(0,"span",38),s.vc(1),s.Qb()),2&n){const n=t.$implicit;s.Bb(1),s.xc(" ",n.name," ")}}function y(n,t){if(1&n&&(s.Rb(0,"div",33),s.uc(1,w,1,1,"img",34),s.Rb(2,"div"),s.vc(3,"Designers:"),s.Qb(),s.Rb(4,"div",35),s.uc(5,x,2,1,"span",36),s.Qb(),s.Qb()),2&n){const n=s.cc(2);s.Bb(1),s.hc("ngForOf",n.game.author),s.Bb(4),s.hc("ngForOf",n.game.author)}}function Q(n,t){if(1&n&&(s.Rb(0,"span",38),s.vc(1),s.Qb()),2&n){const n=t.$implicit;s.Bb(1),s.xc(" ",n.name," ")}}function B(n,t){if(1&n&&(s.Rb(0,"div",33),s.Rb(1,"div"),s.vc(2,"Categories:"),s.Qb(),s.Rb(3,"div",35),s.uc(4,Q,2,1,"span",36),s.Qb(),s.Qb()),2&n){const n=s.cc(2);s.Bb(4),s.hc("ngForOf",n.game.category)}}function k(n,t){if(1&n&&(s.Rb(0,"span",38),s.vc(1),s.Qb()),2&n){const n=t.$implicit;s.Bb(1),s.xc(" ",n.name," ")}}function I(n,t){if(1&n&&(s.Rb(0,"div",33),s.Rb(1,"div"),s.vc(2,"Game Mechanics:"),s.Qb(),s.Rb(3,"div",35),s.uc(4,k,2,1,"span",36),s.Qb(),s.Qb()),2&n){const n=s.cc(2);s.Bb(4),s.hc("ngForOf",n.game.gameMechanic)}}function G(n,t){if(1&n&&(s.Rb(0,"span",38),s.vc(1),s.Qb()),2&n){const n=t.$implicit;s.Bb(1),s.xc(" ",n.name," ")}}function S(n,t){if(1&n&&(s.Rb(0,"div",33),s.Rb(1,"div"),s.vc(2,"Publisher:"),s.Qb(),s.Rb(3,"div",35),s.uc(4,G,2,1,"span",36),s.Qb(),s.Qb()),2&n){const n=s.cc(2);s.Bb(4),s.hc("ngForOf",n.game.publisher)}}function F(n,t){if(1&n&&(s.Rb(0,"section",29),s.Rb(1,"details",30),s.Rb(2,"summary"),s.vc(3,"Categories, Designers, Game Mechanics and Publisher"),s.Qb(),s.Rb(4,"div",31),s.uc(5,y,6,2,"div",32),s.uc(6,B,5,1,"div",32),s.uc(7,I,5,1,"div",32),s.uc(8,S,5,1,"div",32),s.Qb(),s.Qb(),s.Qb()),2&n){const n=s.cc();s.Bb(5),s.hc("ngIf",n.game.author),s.Bb(1),s.hc("ngIf",n.game.category),s.Bb(1),s.hc("ngIf",n.game.gameMechanic),s.Bb(1),s.hc("ngIf",n.game.publisher)}}function L(n,t){if(1&n&&(s.Rb(0,"section",39),s.Rb(1,"div",40),s.Rb(2,"h2"),s.vc(3,"Description"),s.Qb(),s.Rb(4,"p"),s.vc(5),s.Qb(),s.Qb(),s.Rb(6,"details",41),s.Rb(7,"summary"),s.vc(8,"Description"),s.Qb(),s.Rb(9,"p",31),s.vc(10),s.Qb(),s.Qb(),s.Qb()),2&n){const n=s.cc();s.Bb(5),s.wc(n.game.description),s.Bb(5),s.xc(" ",n.game.description," ")}}function A(n,t){1&n&&(s.Rb(0,"section",42),s.Rb(1,"h2"),s.vc(2,"Loading the game details"),s.Qb(),s.Nb(3,"app-loading"),s.Qb())}let N=(()=>{class n{constructor(n,t,e){this.router=n,this.route=t,this.gameStore=e,this.onlineGames=[],this.gameInfos=[],this.bgaInfos=[],this.bggInfos=[],this.rating=0,this.isLoading=!0}ngOnInit(){this.gameStore.isLoadingDetails.subscribe(n=>this.isLoading=n),this.route.queryParams.subscribe(n=>{n.id&&(this.paramId=n.id,this.gameStore.loadBoardGame(this.paramId))}),this.gameStore.getBoardGames.subscribe(n=>{this.paramId&&(this.game=n.find(n=>n.id==this.paramId)),this.createGameInfos()}),this.gameStore.getRatings.subscribe(n=>{this.userRate=n.find(n=>{var t;return n.game===(null===(t=this.game)||void 0===t?void 0:t.id)}),this.rating=this.userRate?this.userRate.rating:0,console.log("User rating:",this.userRate),console.log("New ratings: ",this.rating)}),this.onlineGames=[...this.onlineGames].splice(0,2)}rate(n){this.gameStore.sendRating({game:this.game.id,rating:n})}goToAmazon(){window.open("https://www.amazon.com/s?k="+this.game.name,"_blank")}clickOnOnlinegame(n){window.open("Yucata"===n.origin?"https://"+n.url:n.url,"_blank")}clickOnInfo(n){n.link&&window.open(n.link,"_blank")}removeRating(){var n;(null===(n=this.userRate)||void 0===n?void 0:n.id)&&this.gameStore.deleteRating(this.userRate.id)}getOnlineGameIcon(n){switch(n){case"Tabletopia":return"https://steamcdn-a.akamaihd.net/steam/apps/402560/logo.png?t=1596691394";case"Yucata":return"https://www.yucata.de/bundles/images/Logo.jpg";case"Boardgamearena":return"http://x.boardgamearena.net/data/newsimg/logo2016.png";default:return"https://files.softicons.com/download/game-icons/brain-games-icons-by-quizanswers/png/512x512/Board-Games.png"}}createGameInfos(){this.game&&(this.gameInfos=[],this.bgaInfos=[],this.bggInfos=[],this.game.minNumberOfPlayers&&this.gameInfos.push({icon:"groups",text:this.game.minNumberOfPlayers+" - "+this.game.maxNumberOfPlayers,description:"Number of players"}),this.game.minPlaytime&&this.gameInfos.push({icon:"access_time",text:this.game.minPlaytime+" - "+this.game.maxPlaytime,description:"Playtime in minutes"}),this.game.minAge&&this.gameInfos.push({icon:"person",text:this.game.minAge+"+",description:"Min age"}),this.game.officialUrl&&this.game.officialUrl.length>5&&this.gameInfos.push({icon:"link",text:"Website",description:"Link to official website",link:this.game.officialUrl}),this.game.bggRating&&this.bggInfos.push({icon:"stars",text:"Rating: "+this.game.bggRating.toPrecision(2)}),this.game.bggAvgRating&&this.bggInfos.push({icon:"stars",text:"Average Rating: "+this.game.bggAvgRating.toPrecision(2)}),this.game.bgaRating&&this.bgaInfos.push({icon:"stars",text:"Rating: "+this.game.bgaRating.toPrecision(2)}),this.game.bgaAvgRating&&this.bgaInfos.push({icon:"stars",text:"Average Rating: "+this.game.bgaAvgRating.toPrecision(2)}),this.game.bgaUrl&&this.bgaInfos.push({icon:"link",text:"Go to Website",description:"Link to Board Game Atlas",link:this.game.bgaUrl}))}}return n.\u0275fac=function(t){return new(t||n)(s.Mb(c.c),s.Mb(c.a),s.Mb(r.a))},n.\u0275cmp=s.Gb({type:n,selectors:[["app-detail"]],decls:5,vars:4,consts:[[1,"wrapper","row"],["class","top-section row",4,"ngIf"],["class","info-section row",4,"ngIf"],["class","description-section row",4,"ngIf"],["class","loading",4,"ngIf"],[1,"top-section","row"],[1,"image","col-3"],[3,"src","alt"],[1,"game-info","col-7"],[4,"ngIf"],[1,"info-list"],["class","info-card",3,"matTooltip","ngClass","click",4,"ngFor","ngForOf"],["class","external-container",4,"ngIf"],[1,"actions","col-2"],[3,"numStars","rating","rated"],[1,"buttons"],[1,"primary",3,"disabled","click"],[1,"primary",3,"click"],[1,"info-card",3,"matTooltip","ngClass","click"],[1,"text"],[1,"external-container"],[1,"title"],["src","https://image.winudf.com/v2/image1/Y29tLmF0bGFzYWxwaGEuYm9hcmRnYW1lYXRsYXNfaWNvbl8xNTYyODU4NjE4XzA4NA/icon.png?w=170&fakeurl=1","alt",""],["class","info-row",3,"ngClass","click",4,"ngFor","ngForOf"],[1,"info-row",3,"ngClass","click"],["src","https://pbs.twimg.com/profile_images/1158829646370226176/A2xzJhSc_400x400.jpg","alt",""],["class","info-row link",3,"click",4,"ngFor","ngForOf"],[1,"info-row","link",3,"click"],["alt","",1,"online-game",3,"src"],[1,"info-section","row"],[1,"short-description"],[1,"content"],["class","info-row",4,"ngIf"],[1,"info-row"],["alt","","class","hide hide-on-s hide-on-xs",3,"src",4,"ngFor","ngForOf"],[1,"chip-row"],["class","chip",4,"ngFor","ngForOf"],["alt","",1,"hide","hide-on-s","hide-on-xs",3,"src"],[1,"chip"],[1,"description-section","row"],[1,"hide","hide-on-s","hide-on-xs"],[1,"hide-on-l","hide-on-xl"],[1,"loading"]],template:function(n,t){1&n&&(s.Rb(0,"div",0),s.uc(1,_,19,11,"section",1),s.uc(2,F,9,4,"section",2),s.uc(3,L,11,2,"section",3),s.uc(4,A,4,0,"section",4),s.Qb()),2&n&&(s.Bb(1),s.hc("ngIf",t.game&&!t.isLoading),s.Bb(1),s.hc("ngIf",t.game&&!t.isLoading&&(t.game.author||t.game.category||t.game.gameMechanic||t.game.publisher)),s.Bb(1),s.hc("ngIf",t.game&&t.game.description&&!t.isLoading),s.Bb(1),s.hc("ngIf",t.isLoading))},directives:[i.k,i.j,l,b.a,i.i,g.a,h],styles:[".wrapper[_ngcontent-%COMP%]{margin-top:4rem;padding:0 .25rem}.top-section[_ngcontent-%COMP%]   img[_ngcontent-%COMP%]{width:100%;border-radius:10px}.top-section[_ngcontent-%COMP%]   .game-info[_ngcontent-%COMP%]{padding-left:1rem}.top-section[_ngcontent-%COMP%]   .game-info[_ngcontent-%COMP%]   .info-list[_ngcontent-%COMP%]{display:flex;flex-direction:row;flex-wrap:wrap}.top-section[_ngcontent-%COMP%]   .game-info[_ngcontent-%COMP%]   .info-list[_ngcontent-%COMP%]   .info-card[_ngcontent-%COMP%]{padding:.5rem 1rem;display:flex;margin:.5rem;flex-direction:column;align-items:center;background:#d1e3f1;border-radius:10px;justify-content:center;transition:background-color .3s}.top-section[_ngcontent-%COMP%]   .game-info[_ngcontent-%COMP%]   .info-list[_ngcontent-%COMP%]   .link[_ngcontent-%COMP%]{cursor:pointer}.top-section[_ngcontent-%COMP%]   .game-info[_ngcontent-%COMP%]   .info-list[_ngcontent-%COMP%]   .link[_ngcontent-%COMP%]:hover{background:#aacbe5}.top-section[_ngcontent-%COMP%]   .game-info[_ngcontent-%COMP%]   .external-container[_ngcontent-%COMP%]{padding:.5rem 1rem;display:flex;margin:.75rem .5rem;flex-direction:column;background:#d1e3f1;border-radius:10px;max-width:20rem}.top-section[_ngcontent-%COMP%]   .game-info[_ngcontent-%COMP%]   .external-container[_ngcontent-%COMP%]   img.online-game[_ngcontent-%COMP%]{width:3rem;height:3rem;margin-right:1rem}.top-section[_ngcontent-%COMP%]   .game-info[_ngcontent-%COMP%]   .external-container[_ngcontent-%COMP%]   .title[_ngcontent-%COMP%]{display:flex;margin-bottom:1rem}.top-section[_ngcontent-%COMP%]   .game-info[_ngcontent-%COMP%]   .external-container[_ngcontent-%COMP%]   .title[_ngcontent-%COMP%]   img[_ngcontent-%COMP%]{width:3rem;height:3rem;margin-right:1rem}.top-section[_ngcontent-%COMP%]   .game-info[_ngcontent-%COMP%]   .external-container[_ngcontent-%COMP%]   .title[_ngcontent-%COMP%]   .text[_ngcontent-%COMP%]{align-self:center;font-weight:600;font-size:1.1rem}.top-section[_ngcontent-%COMP%]   .game-info[_ngcontent-%COMP%]   .external-container[_ngcontent-%COMP%]   .info-row[_ngcontent-%COMP%]{display:flex;padding:.5rem;border-radius:10px}.top-section[_ngcontent-%COMP%]   .game-info[_ngcontent-%COMP%]   .external-container[_ngcontent-%COMP%]   .info-row[_ngcontent-%COMP%]   mat-icon[_ngcontent-%COMP%]{margin-right:.5rem}.top-section[_ngcontent-%COMP%]   .link[_ngcontent-%COMP%]{cursor:pointer;transition:background-color .3s}.top-section[_ngcontent-%COMP%]   .link[_ngcontent-%COMP%]:hover{background:#aacbe5}.top-section[_ngcontent-%COMP%]   .actions[_ngcontent-%COMP%]{display:flex;flex-direction:column;justify-content:space-evenly;margin:1rem 0}.top-section[_ngcontent-%COMP%]   .actions[_ngcontent-%COMP%]   mat-icon[_ngcontent-%COMP%]{font-size:3rem}.top-section[_ngcontent-%COMP%]   .actions[_ngcontent-%COMP%]   .buttons[_ngcontent-%COMP%]{margin-top:1rem;align-self:center}.top-section[_ngcontent-%COMP%]   .actions[_ngcontent-%COMP%]   .buttons[_ngcontent-%COMP%]   button[_ngcontent-%COMP%]{margin:.5rem}.description-section[_ngcontent-%COMP%]{padding:.5rem;margin:.5rem .5rem 3rem}.game-section[_ngcontent-%COMP%]{margin:5rem 0;padding:.5rem;background-color:#d1e3f1;border-radius:10px}.game-section[_ngcontent-%COMP%]   .game-list[_ngcontent-%COMP%]{display:flex;flex-wrap:nowrap;overflow-x:auto}.info-section[_ngcontent-%COMP%]{padding:.5rem;margin:.5rem}.info-section[_ngcontent-%COMP%]   .info-row[_ngcontent-%COMP%]{margin:.6rem 0}.info-section[_ngcontent-%COMP%]   .info-row[_ngcontent-%COMP%]   .chip-row[_ngcontent-%COMP%]{display:flex;flex-direction:row;overflow:auto}.info-section[_ngcontent-%COMP%]   .info-row[_ngcontent-%COMP%]   .chip-row[_ngcontent-%COMP%]   .chip[_ngcontent-%COMP%]{background:#fff;margin:.3rem;padding:.3rem .8rem;border-radius:10px;white-space:nowrap}.loading[_ngcontent-%COMP%]{padding:1rem;display:flex;flex-direction:column;align-items:center}@media only screen and (min-width:992px){.top-section[_ngcontent-%COMP%], .wrapper[_ngcontent-%COMP%]{padding:2rem}.top-section[_ngcontent-%COMP%]   .actions[_ngcontent-%COMP%]   .buttons[_ngcontent-%COMP%]{margin-top:2rem;align-self:flex-end}.info-row[_ngcontent-%COMP%]   img[_ngcontent-%COMP%]{height:10rem}.info-row[_ngcontent-%COMP%]   .chip-row[_ngcontent-%COMP%]{display:flex;flex-direction:row;overflow:hidden;flex-wrap:wrap}.description-section[_ngcontent-%COMP%]{padding:0 3rem}}"]}),n})();var Y=e("JX91"),D=e("lJxs"),j=e("e6WT");function T(n,t){if(1&n){const n=s.Sb();s.Pb(0),s.Rb(1,"app-star-rating",4),s.Yb("rated",function(t){return s.mc(n),s.cc().rate(t)}),s.Qb(),s.Ob()}if(2&n){const n=s.cc();s.Bb(1),s.hc("numStars",10)("rating",n.rating)}}let $=(()=>{class n{constructor(n,t,e){this.router=n,this.route=t,this.gameStore=e,this.activateDetails=!1,this.activateRating=!1,this.rated=new s.o}ngOnInit(){}rate(n){this.gameStore.sendRating({game:this.game.id,rating:n}),this.rated.emit({game:this.game.id,rating:n})}openDetails(){this.router.navigate(["detail"],{relativeTo:this.route.parent,queryParams:{id:this.game.id}})}}return n.\u0275fac=function(t){return new(t||n)(s.Mb(c.c),s.Mb(c.a),s.Mb(r.a))},n.\u0275cmp=s.Gb({type:n,selectors:[["app-game-card"]],inputs:{game:"game",rating:"rating",activateDetails:"activateDetails",activateRating:"activateRating"},outputs:{rated:"rated"},decls:5,vars:5,consts:[[1,"card"],[3,"src","alt","ngClass","click"],[4,"ngIf"],[1,"name"],[1,"rating",3,"numStars","rating","rated"]],template:function(n,t){1&n&&(s.Rb(0,"div",0),s.Rb(1,"img",1),s.Yb("click",function(){return t.activateDetails&&t.openDetails()}),s.Qb(),s.uc(2,T,2,2,"ng-container",2),s.Rb(3,"div",3),s.vc(4),s.Qb(),s.Qb()),2&n&&(s.Bb(1),s.hc("src",t.game.imageUrl,s.nc)("alt",t.game.name)("ngClass",t.activateDetails?"activatedDetails":""),s.Bb(1),s.hc("ngIf",t.activateRating),s.Bb(2),s.wc(t.game.name))},directives:[i.i,i.k,l],styles:[".card[_ngcontent-%COMP%]{display:flex;flex-direction:column;width:10rem;margin-bottom:1.5rem}img[_ngcontent-%COMP%]{width:9rem;height:9rem;margin:0 auto;border-radius:10px;box-shadow:0 0 15px #afafaf}.name[_ngcontent-%COMP%]{text-align:center;font-size:.95rem}.rating[_ngcontent-%COMP%]{margin-top:5px}.activatedDetails[_ngcontent-%COMP%]:hover{transform:scale(.99);box-shadow:0 0 10px #c5c5c5;cursor:pointer}.activatedDetails[_ngcontent-%COMP%]:active{cursor:pointer;transform:scale(.98)}@media only screen and (min-width:992px){.card[_ngcontent-%COMP%]{margin:1rem;width:18rem}img[_ngcontent-%COMP%]{width:16rem;height:16rem}.name[_ngcontent-%COMP%]{font-size:1rem}}"]}),n})();function z(n,t){if(1&n&&(s.Rb(0,"h2"),s.vc(1),s.Qb()),2&n){const n=s.cc(2);s.Bb(1),s.xc("Rate\xa0",5-n.ratings.length<0?0:5-n.ratings.length,"\xa0 more games that you like or dislike")}}function K(n,t){if(1&n){const n=s.Sb();s.Rb(0,"section",5),s.uc(1,z,2,1,"h2",3),s.Rb(2,"div",6),s.Rb(3,"label",7),s.vc(4,"Search for games"),s.Qb(),s.Rb(5,"span",8),s.Nb(6,"input",9),s.Rb(7,"div",10),s.Rb(8,"button",11),s.Yb("click",function(){return s.mc(n),s.cc().next()}),s.vc(9," Next "),s.Rb(10,"mat-icon"),s.vc(11,"chevron_right"),s.Qb(),s.Qb(),s.Qb(),s.Qb(),s.Qb(),s.Qb()}if(2&n){const n=s.cc();s.Bb(1),s.hc("ngIf",5-n.ratings.length>0),s.Bb(5),s.hc("formControl",n.searchControl),s.Bb(1),s.hc("matTooltip","Please rate at least"+(5-n.ratings.length)+" more games")("matTooltipDisabled",n.ratings.length>=5),s.Bb(1),s.hc("disabled",n.ratings.length<5)}}function U(n,t){if(1&n&&(s.Rb(0,"div"),s.Nb(1,"app-game-card",13),s.Qb()),2&n){const n=t.$implicit,e=s.cc(2);s.Bb(1),s.hc("game",n)("rating",e.getRatingForGame(n.id))("activateDetails",!0)("activateRating",!0)}}function J(n,t){if(1&n&&(s.Pb(0),s.uc(1,U,2,4,"div",12),s.dc(2,"async"),s.Ob()),2&n){const n=s.cc();s.Bb(1),s.hc("ngForOf",s.ec(2,1,n.filteredGames))}}function W(n,t){1&n&&(s.Rb(0,"section",14),s.Rb(1,"h2"),s.vc(2,"Give us a second, we are loading all the great games."),s.Qb(),s.Nb(3,"app-loading"),s.Qb())}let E=(()=>{class n{constructor(n,t,e){this.router=n,this.route=t,this.gameStore=e,this.searchControl=new o.c,this.ratings=[],this.isLoading=!0,this.isLoadingRecommendations=!1}ngOnInit(){this.gameStore.getRatings.subscribe(n=>this.ratings=n),this.gameStore.isLoadingRecommendations.subscribe(n=>this.isLoadingRecommendations=n),this.gameStore.isLoading.subscribe(n=>this.isLoading=n),this.gameStore.getBoardGames.subscribe(n=>{this.games=n,this.filteredGames=this.searchControl.valueChanges.pipe(Object(Y.a)(""),Object(D.a)(n=>this._filter(n)),Object(D.a)(n=>n.slice(0,15)))})}getRatingForGame(n){const t=this.ratings.find(t=>t.game===n);return t?t.rating:0}next(){this.router.navigate(["recommendations"],{relativeTo:this.route}),this.isLoadingRecommendations||(this.gameStore.loadRecommendedCommonBased(),this.gameStore.loadRecommendedItemBased(),this.gameStore.loadRecommendedKNN(),this.gameStore.loadRecommendedPopularity())}_filter(n){const t=this._normalizeValue(n);return this.games.filter(n=>this._normalizeValue(n.name).includes(t))}_normalizeValue(n){return n.toLowerCase().replace(/\s/g,"")}}return n.\u0275fac=function(t){return new(t||n)(s.Mb(c.c),s.Mb(c.a),s.Mb(r.a))},n.\u0275cmp=s.Gb({type:n,selectors:[["app-questionnaire"]],decls:5,vars:3,consts:[[1,"wrapper","row"],["class","search-section row",4,"ngIf"],[1,"game-list","row"],[4,"ngIf"],["class","loading",4,"ngIf"],[1,"search-section","row"],[1,"input-section","col-xl-4"],["for","search"],[1,"input-line"],["matInput","","type","text","autofocus","","placeholder","Search...",1,"search-input",3,"formControl"],[3,"matTooltip","matTooltipDisabled"],[1,"primary",3,"disabled","click"],[4,"ngFor","ngForOf"],[3,"game","rating","activateDetails","activateRating"],[1,"loading"]],template:function(n,t){1&n&&(s.Rb(0,"div",0),s.uc(1,K,12,5,"section",1),s.Rb(2,"section",2),s.uc(3,J,3,3,"ng-container",3),s.Qb(),s.uc(4,W,4,0,"section",4),s.Qb()),2&n&&(s.Bb(1),s.hc("ngIf",!t.isLoading),s.Bb(2),s.hc("ngIf",!t.isLoading),s.Bb(1),s.hc("ngIf",t.isLoading))},directives:[i.k,j.a,o.a,o.j,o.d,b.a,g.a,i.j,$,h],pipes:[i.b],styles:[".wrapper[_ngcontent-%COMP%]{margin-top:4rem}.search-section[_ngcontent-%COMP%]{display:flex;flex-direction:column;padding:.5rem;margin:.5rem;border-radius:10px;align-items:center}.search-section[_ngcontent-%COMP%]   .input-line[_ngcontent-%COMP%]{display:flex}.search-section[_ngcontent-%COMP%]   .input-line[_ngcontent-%COMP%]   .search-input[_ngcontent-%COMP%]{width:100%;float:left}.search-section[_ngcontent-%COMP%]   .input-line[_ngcontent-%COMP%]   div[_ngcontent-%COMP%]{display:flex}.search-section[_ngcontent-%COMP%]   .input-line[_ngcontent-%COMP%]   div[_ngcontent-%COMP%]   button[_ngcontent-%COMP%]{margin-left:.5rem;float:right}.game-list[_ngcontent-%COMP%]{justify-content:center}.game-list[_ngcontent-%COMP%], .loading[_ngcontent-%COMP%]{display:flex;flex-direction:column;align-items:center}.loading[_ngcontent-%COMP%]{padding:1rem}@media only screen and (min-width:768px){.search-section[_ngcontent-%COMP%], .wrapper[_ngcontent-%COMP%]{padding:2rem}.game-list[_ngcontent-%COMP%]{flex-wrap:wrap;flex-direction:row}}"]}),n})();var q=e("Dxy4");function V(n,t){if(1&n){const n=s.Sb();s.Rb(0,"section",20),s.Rb(1,"div",21),s.Rb(2,"button",22),s.Yb("click",function(){return s.mc(n),s.cc().refresh()}),s.Rb(3,"mat-icon"),s.vc(4,"autorenew"),s.Qb(),s.Qb(),s.Qb(),s.Qb()}if(2&n){const n=s.cc();s.Bb(1),s.hc("matTooltip",n.isLoadingRecommendations?"Loading all your recommendations...":"Refresh recommendations!"),s.Bb(1),s.hc("disabled",n.isLoadingRecommendations)}}function X(n,t){1&n&&s.Nb(0,"app-game-card",26),2&n&&s.hc("game",t.$implicit)("activateDetails",!0)}function Z(n,t){if(1&n&&(s.Rb(0,"section",23),s.Rb(1,"h1"),s.vc(2,"Top Picks for you"),s.Qb(),s.Rb(3,"div",24),s.uc(4,X,1,2,"app-game-card",25),s.Qb(),s.Qb()),2&n){const n=s.cc();s.Bb(4),s.hc("ngForOf",n.knn)}}function H(n,t){1&n&&s.Nb(0,"app-game-card",26),2&n&&s.hc("game",t.$implicit)("activateDetails",!0)}function nn(n,t){if(1&n&&(s.Rb(0,"section",23),s.Rb(1,"h1"),s.vc(2,"Users similar to you also liked"),s.Qb(),s.Rb(3,"div",24),s.uc(4,H,1,2,"app-game-card",25),s.Qb(),s.Qb()),2&n){const n=s.cc();s.Bb(4),s.hc("ngForOf",n.commonBased)}}function tn(n,t){1&n&&s.Nb(0,"app-game-card",26),2&n&&s.hc("game",t.$implicit)("activateDetails",!0)}function en(n,t){if(1&n&&(s.Rb(0,"section",23),s.Rb(1,"h1"),s.vc(2,"Games similar to your favorite games"),s.Qb(),s.Rb(3,"div",24),s.uc(4,tn,1,2,"app-game-card",25),s.Qb(),s.Qb()),2&n){const n=s.cc();s.Bb(4),s.hc("ngForOf",n.itemBased)}}function an(n,t){1&n&&s.Nb(0,"app-game-card",26),2&n&&s.hc("game",t.$implicit)("activateDetails",!0)}function on(n,t){if(1&n&&(s.Rb(0,"section",23),s.Rb(1,"h1"),s.vc(2,"Trending"),s.Qb(),s.Rb(3,"div",24),s.uc(4,an,1,2,"app-game-card",25),s.Qb(),s.Qb()),2&n){const n=s.cc();s.Bb(4),s.hc("ngForOf",n.popularity)}}function cn(n,t){1&n&&(s.Rb(0,"section",27),s.Rb(1,"h2"),s.vc(2,"We are looking for games you will love!"),s.Qb(),s.Nb(3,"app-loading"),s.Qb())}function sn(n,t){if(1&n&&(s.Rb(0,"div"),s.Nb(1,"app-game-card",5),s.Qb()),2&n){const n=t.$implicit,e=s.cc(2);s.Bb(1),s.hc("game",n)("rating",e.getRatingForGame(n.id))("activateDetails",!0)("activateRating",!0)}}function rn(n,t){if(1&n&&(s.Pb(0),s.uc(1,sn,2,4,"div",4),s.Ob()),2&n){const n=s.cc();s.Bb(1),s.hc("ngForOf",n.ratedGames)}}function gn(n,t){1&n&&(s.Rb(0,"section",6),s.Rb(1,"h2"),s.vc(2,"Give us a second, we are loading all the great games."),s.Qb(),s.Nb(3,"app-loading"),s.Qb())}const mn=[{path:"recommendations",component:(()=>{class n{constructor(n){this.gameStore=n,this.commonBased=[],this.knn=[],this.itemBased=[],this.popularity=[],this.gameMap=new Map,this.isLoading=!1,this.isLoadingRecommendations=!1,this.largeScreen=document.body.clientWidth>=992,this.minimumAge=0,this.player={min:0,max:0},this.time={min:0,max:0}}ngOnInit(){window.addEventListener("resize",n=>{this.largeScreen=document.body.clientWidth>=992}),this.gameStore.isLoading.subscribe(n=>this.isLoading=n),this.gameStore.isLoadingRecommendations.subscribe(n=>this.isLoadingRecommendations=n),this.gameStore.getBoardGames.subscribe(n=>{this.gameStore.getRecommendedBoardGames.subscribe(t=>{n.forEach(n=>this.gameMap.set(n.id,n)),this.recommendations=t,this.commonBased=this.getGameListFromKeys(t.commonBased,this.gameMap),this.knn=this.getGameListFromKeys(t.knn,this.gameMap),this.itemBased=this.getGameListFromKeys(t.itemBased,this.gameMap),this.popularity=this.getGameListFromKeys(t.popularity,this.gameMap)})})}getGameListFromKeys(n,t){const e=[];if(n.length>0)for(let i=0;i<50&&n[i];i++){const a=t.get(n[i].gameKey);a&&e.push(a)}return e}minusMinAge(){this.minimumAge=this.minimumAge<0?-1:this.minimumAge-1}plusMinAge(){this.minimumAge=this.minimumAge>99?100:this.minimumAge+1}refresh(){this.gameStore.loadRecommendedPopularity(),this.gameStore.loadRecommendedKNN(),this.gameStore.loadRecommendedItemBased(),this.gameStore.loadRecommendedCommonBased()}resetFilter(){this.minimumAge=0,this.player={min:0,max:0},this.time={min:0,max:0},this.filter()}filter(){const n=new Map;this.gameMap.forEach((t,e)=>{(0===this.minimumAge||t.minAge&&t.minAge>=this.minimumAge)&&(0===this.player.min||t.minNumberOfPlayers&&t.minNumberOfPlayers>=this.player.min&&t.minNumberOfPlayers<=this.player.max)&&(0===this.player.max||t.maxNumberOfPlayers&&t.maxNumberOfPlayers<=this.player.max&&t.maxNumberOfPlayers>=this.player.min)&&(0===this.time.min||t.minPlaytime&&t.minPlaytime>=this.time.min&&t.minPlaytime<=this.player.max)&&(0===this.time.max||t.maxPlaytime&&t.maxPlaytime<=this.time.max&&t.maxPlaytime>=this.time.min)&&n.set(e,t)}),this.commonBased=this.getGameListFromKeys(this.recommendations.commonBased,n),this.knn=this.getGameListFromKeys(this.recommendations.knn,n),this.itemBased=this.getGameListFromKeys(this.recommendations.itemBased,n),this.popularity=this.getGameListFromKeys(this.recommendations.popularity,n)}}return n.\u0275fac=function(t){return new(t||n)(s.Mb(r.a))},n.\u0275cmp=s.Gb({type:n,selectors:[["app-recommendation"]],decls:50,vars:13,consts:[[1,"wrapper","row"],[1,"filter-section"],[1,"filter","col-l-2","col-xl-2",3,"open"],[1,"content","filter"],[1,"input-section"],["for","age"],[1,"num-input"],["mat-icon-button","","color","primary",3,"click"],["name","minimumAge","type","number","min","0","max","99",1,"input",3,"ngModel","ngModelChange"],["age",""],["type","number","min","0","max","49",1,"input",3,"ngModel","ngModelChange"],["type","number","min","1","max","50",1,"input",3,"ngModel","ngModelChange"],["type","number","min","0","max","999",1,"input",3,"ngModel","ngModelChange"],["type","number","min","1","max","1000",1,"input",3,"ngModel","ngModelChange"],[1,"filter-actions"],[1,"button","primary",3,"click"],[3,"matTooltip","click"],["class","col-l-10 action-section",4,"ngIf"],["class","game-section col-l-10",4,"ngIf"],["class","loading",4,"ngIf"],[1,"col-l-10","action-section"],[1,"tooltip",3,"matTooltip"],[1,"primary",3,"disabled","click"],[1,"game-section","col-l-10"],[1,"game-row"],[3,"game","activateDetails",4,"ngFor","ngForOf"],[3,"game","activateDetails"],[1,"loading"]],template:function(n,t){1&n&&(s.Rb(0,"div",0),s.Rb(1,"section",1),s.Rb(2,"details",2),s.Rb(3,"summary"),s.vc(4," Filter "),s.Qb(),s.Rb(5,"div",3),s.Rb(6,"div",4),s.Rb(7,"label",5),s.vc(8,"Minimum Age"),s.Qb(),s.Rb(9,"div",6),s.Rb(10,"button",7),s.Yb("click",function(){return t.minusMinAge()}),s.Rb(11,"mat-icon"),s.vc(12,"remove"),s.Qb(),s.Qb(),s.Rb(13,"input",8,9),s.Yb("ngModelChange",function(n){return t.minimumAge<0?void 0:t.minimumAge=n}),s.Qb(),s.Rb(15,"button",7),s.Yb("click",function(){return t.plusMinAge()}),s.Rb(16,"mat-icon"),s.vc(17,"add"),s.Qb(),s.Qb(),s.Qb(),s.Qb(),s.Rb(18,"div",4),s.Rb(19,"label",5),s.vc(20,"Player"),s.Qb(),s.Rb(21,"div",6),s.Rb(22,"input",10,9),s.Yb("ngModelChange",function(n){return t.player.min=n}),s.Qb(),s.vc(24," \xa0-\xa0 "),s.Rb(25,"input",11,9),s.Yb("ngModelChange",function(n){return t.player.max=n}),s.Qb(),s.Qb(),s.Qb(),s.Rb(27,"div",4),s.Rb(28,"label",5),s.vc(29,"Playtime"),s.Qb(),s.Rb(30,"div",6),s.Rb(31,"input",12,9),s.Yb("ngModelChange",function(n){return t.time.min=n}),s.Qb(),s.vc(33," \xa0-\xa0 "),s.Rb(34,"input",13,9),s.Yb("ngModelChange",function(n){return t.time.max=n}),s.Qb(),s.Qb(),s.Qb(),s.Rb(36,"div",14),s.Rb(37,"button",15),s.Yb("click",function(){return t.filter()}),s.Rb(38,"mat-icon"),s.vc(39,"filter_alt"),s.Qb(),s.vc(40," Filter "),s.Qb(),s.Rb(41,"button",16),s.Yb("click",function(){return t.resetFilter()}),s.Rb(42,"mat-icon"),s.vc(43,"delete"),s.Qb(),s.Qb(),s.Qb(),s.Qb(),s.Qb(),s.Qb(),s.uc(44,V,5,2,"section",17),s.uc(45,Z,5,1,"section",18),s.uc(46,nn,5,1,"section",18),s.uc(47,en,5,1,"section",18),s.uc(48,on,5,1,"section",18),s.uc(49,cn,4,0,"section",19),s.Qb()),2&n&&(s.Bb(2),s.hc("open",t.largeScreen),s.Bb(11),s.hc("ngModel",t.minimumAge<0?void 0:t.minimumAge),s.Bb(9),s.hc("ngModel",t.player.min),s.Bb(3),s.hc("ngModel",t.player.max),s.Bb(6),s.hc("ngModel",t.time.min),s.Bb(3),s.hc("ngModel",t.time.max),s.Bb(7),s.hc("matTooltip","Remove all Filters"),s.Bb(3),s.hc("ngIf",!t.isLoading),s.Bb(1),s.hc("ngIf",!t.isLoading&&t.knn.length>0),s.Bb(1),s.hc("ngIf",!t.isLoading&&t.commonBased.length>0),s.Bb(1),s.hc("ngIf",!t.isLoading&&t.itemBased.length>0),s.Bb(1),s.hc("ngIf",!t.isLoading),s.Bb(1),s.hc("ngIf",t.isLoading))},directives:[q.a,g.a,o.n,o.a,o.j,o.m,b.a,i.k,i.j,$,h],styles:[".wrapper[_ngcontent-%COMP%]{margin-top:4rem}.filter[_ngcontent-%COMP%]{padding:.2rem}.filter[_ngcontent-%COMP%]   .num-input[_ngcontent-%COMP%]{align-self:center;font-weight:500}.filter[_ngcontent-%COMP%]   .filter-actions[_ngcontent-%COMP%]{text-align:center;margin:1rem 0}.action-section[_ngcontent-%COMP%]{text-align:center;margin:.5rem 0}.action-section[_ngcontent-%COMP%]   .tooltip[_ngcontent-%COMP%]{display:inline-flex}.game-section[_ngcontent-%COMP%]{margin-bottom:.3rem}.game-section[_ngcontent-%COMP%]   h1[_ngcontent-%COMP%]{padding:0 .5rem}.game-section[_ngcontent-%COMP%]   .game-row[_ngcontent-%COMP%]{display:flex;flex-direction:row;flex-wrap:nowrap;overflow-x:auto;background:#fff}.game-section[_ngcontent-%COMP%]   .game-row[_ngcontent-%COMP%]   [_ngcontent-%COMP%]::-webkit-scrollbar{width:0;background:transparent;height:.5rem}.game-section[_ngcontent-%COMP%]   .game-row[_ngcontent-%COMP%]   [_ngcontent-%COMP%]::-webkit-scrollbar-thumb{background:#d1e3f1;border-radius:10px}.loading[_ngcontent-%COMP%]{padding:1rem;display:flex;flex-direction:column;align-items:center}@media only screen and (min-width:992px){.wrapper[_ngcontent-%COMP%]{padding:1rem}.filter-section[_ngcontent-%COMP%]{padding:1rem 0}.action-section[_ngcontent-%COMP%]{text-align:left;margin:0}.action-section[_ngcontent-%COMP%], .game-section[_ngcontent-%COMP%]{float:right;padding:1rem}.game-section[_ngcontent-%COMP%]   [_ngcontent-%COMP%]::-webkit-scrollbar{width:0;background:transparent;height:.5rem}.game-section[_ngcontent-%COMP%]   [_ngcontent-%COMP%]::-webkit-scrollbar-thumb{background:#d1e3f1;border-radius:10px}.filter-section[_ngcontent-%COMP%]   details[_ngcontent-%COMP%]{position:fixed}.filter-section[_ngcontent-%COMP%]   .filter[_ngcontent-%COMP%]   .num-input[_ngcontent-%COMP%]{font-weight:500;align-items:baseline;display:flex}details[_ngcontent-%COMP%]   summary[_ngcontent-%COMP%]{display:none}details[_ngcontent-%COMP%]   .content[_ngcontent-%COMP%]{border-radius:10px}}"]}),n})()},{path:"detail",component:N},{path:"user-ratings",component:(()=>{class n{constructor(n){this.gameStore=n,this.isLoading=!1,this.allGames=new Map,this.ratings=[]}ngOnInit(){this.gameStore.isLoading.subscribe(n=>this.isLoading=n),this.gameStore.getRatings.subscribe(n=>this.ratings=n),this.gameStore.getBoardGames.subscribe(n=>{n.forEach(n=>this.allGames.set(n.id,n)),this.ratedGames=this._getRatedGames()})}getRatingForGame(n){var t;return null===(t=this.ratings.find(t=>t.game===n))||void 0===t?void 0:t.rating}_getRatedGames(){const n=new Map;return this.ratings.forEach(t=>{this.allGames.has(t.game)&&n.set(t.game,this.allGames.get(t.game))}),Array.from(n.values())}}return n.\u0275fac=function(t){return new(t||n)(s.Mb(r.a))},n.\u0275cmp=s.Gb({type:n,selectors:[["app-user-ratings"]],decls:6,vars:2,consts:[[1,"wrapper","row"],[1,"game-list","row"],[4,"ngIf"],["class","loading",4,"ngIf"],[4,"ngFor","ngForOf"],[3,"game","rating","activateDetails","activateRating"],[1,"loading"]],template:function(n,t){1&n&&(s.Rb(0,"div",0),s.Rb(1,"h1"),s.vc(2,"These are all your ratings: "),s.Qb(),s.Rb(3,"section",1),s.uc(4,rn,2,1,"ng-container",2),s.Qb(),s.uc(5,gn,4,0,"section",3),s.Qb()),2&n&&(s.Bb(4),s.hc("ngIf",!t.isLoading),s.Bb(1),s.hc("ngIf",t.isLoading))},directives:[i.k,i.j,$,h],styles:[".wrapper[_ngcontent-%COMP%]{margin-top:4rem}.game-list[_ngcontent-%COMP%]{display:flex;flex-direction:column;justify-content:center;align-items:center}h1[_ngcontent-%COMP%]{padding:0 .5rem}.loading[_ngcontent-%COMP%]{padding:1rem;display:flex;flex-direction:column;align-items:center}@media only screen and (min-width:768px){.wrapper[_ngcontent-%COMP%]{padding:2rem}.game-list[_ngcontent-%COMP%]{flex-wrap:wrap;flex-direction:row}}"]}),n})()},{path:"",component:E}];let ln=(()=>{class n{}return n.\u0275mod=s.Kb({type:n}),n.\u0275inj=s.Jb({factory:function(t){return new(t||n)},imports:[[c.f.forChild(mn)],c.f]}),n})(),bn=(()=>{class n{}return n.\u0275mod=s.Kb({type:n}),n.\u0275inj=s.Jb({factory:function(t){return new(t||n)},imports:[[i.c,a.a,ln,o.g,o.o]]}),n})()}}]);