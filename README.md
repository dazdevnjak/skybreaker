# TODO List

## Scene
- [ ] Meni scena i rezultat scena

## UI
- [ ] Dodati interfejs za dzojstik
- [ ] Prikazivanje tutorial za kretanje 
- [ ] Zvuk za UI

## Sound
- [x] Dodati sistem za zvuk
- [ ] Zvukovi se povremeno poklope a ne mogu da se puste u isto vreme
- [ ] Utisati zvuk za On damage
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
- [ ] Nekad neprijatelj zabaguje i nece da pusti animaciju za eksploziju

## Bomba
- [x] Igrac je dobija kada pokupi pickup, ona trosi vise hp-a od regularnog metka ali na treba na neki poseban nacin da se lansira(npr. ide koso zajedno sa paralaksom ili je teska pa posle kratkog vremena letenja pada)
- [x] Treba da se popravi pozivija za item kada se unisti neprijatelja
- [x] Bomba ne radi damage playerima!

## Stage
- [ ] Dodati mogucnost igranja igre sa tutorijalima i bez njih
- [x] Dodati postepeno otezavanje igre(recimo prvih 10-ak sekundi se igraci medjusobno pucaju zatim krece stvaranje projektila sa strane, nakon 10-ak sekunda se stvara neprijatelj...)
- [ ] Tutorijal nivo (ikonama objasniti igracima koje komande treba da se koriste za odredjene akcije)

## Projectiles
- [x] Popraviti stvaranje projektila, povremeno se desi da se stvori dva projektila na vrlo maloj razlici na z osi sto deluje dosta neprirodno