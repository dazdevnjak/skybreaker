# TODO List

## Scene
- [x] Meni scena i rezultat scena
- [x] Fade in Fade out na scenama rade

## UI
- [x] Dodati interfejs za dzojstik
- [ ] Zvuk za UI
- [x] Dodati interfejs za kontrole prilikom biranja imena
- [ ] Mozda dodati i imena iznad playera

## Sound
- [x] Dodati sistem za zvuk
- [x] Zvukovi se povremeno poklope a ne mogu da se puste u isto vreme
- [x] Utisati zvuk za On damage
- [x] Naci zvukove 

## Player
- [x] Dodati 3 zivota
- [x] Dodati UI za 3 zivota 
- [x] Na smrt resetovati i staviti nevidljivost na malo duzi period 
- [x] Dodati animaciju ili efekat eksplozije kada player umre
- [x] Postaviti da kada pokupi bombu prvi metak koji ispaljuje bude bomba a tek posle toka obican bullet

## Enemy
- [x] Stvaranje posle 15-ak sekundi(proizvoljno) / neki tajmer u main-u koji ce inicijalizovati vreme koje treba da istekne da bi se neprijatelj stvorio(Svuda dodati proveru za None)
- [x] Napravljena je klasa za pickup(collectable) potrebno je dodati da kada se neprijatelj unisti on ispusti pickup koji kada neki od igraca pokupi on dobije jednu BOBMU.
- [x] Napraviti novi sprite sheet za neprijatelja
- [x] Dodati animaciju ili efekat ekspolzije kada enemy umre
- [x] Napraviti da se neprijatelj stvara van ekrana i ulazi u njega, a ne da se stvori na sredini ekrana
- [x] Neprijatelj se ucitava na drugom Thread-u kako bi izbegli stutter
- [ ] Povremeno skloniti Enemy-ja sa scene pa ga vratiti, kako bi u nekom trenutku ostali igraci nasamo cak i ako nije unisten
- [ ] Kada je Enemy unisten treba opet da se pojavi nakon nekog vremena

## Bomba
- [x] Igrac je dobija kada pokupi pickup, ona trosi vise hp-a od regularnog metka ali na treba na neki poseban nacin da se lansira(npr. ide koso zajedno sa paralaksom ili je teska pa posle kratkog vremena letenja pada)
- [x] Treba da se popravi pozivija za item kada se unisti neprijatelja
- [x] Bomba ne radi damage playerima!

## Stage
- [x] Dodati mogucnost igranja igre sa tutorijalima i bez njih
- [x] Dodati postepeno otezavanje igre(recimo prvih 10-ak sekundi se igraci medjusobno pucaju zatim krece stvaranje projektila sa strane, nakon 10-ak sekunda se stvara neprijatelj...)
- [x] Tutorijal nivo (ikonama objasniti igracima koje komande treba da se koriste za odredjene akcije)
- [x] Dodati mogucnost da kada oba igraca drze O na dzojstiku tutorijal se zavrsa i igra pocinje ispocetka bez UI za komande

## Projectiles
- [x] Popraviti stvaranje projektila, povremeno se desi da se stvori dva projektila na vrlo maloj razlici na z osi sto deluje dosta neprirodno
- [x] Dodati koliziju za ispaljene projektile koje dolaze sa strane.
- [ ] Meci ponekad ne uniste projektile?