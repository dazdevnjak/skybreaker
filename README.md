# TODO List

## Scene
- [ ] Meni scena i rezultat scena

## UI
- [ ] Dodati interfejs za dzojstik
- [ ] Prikazivanje tutorial za kretanje 

## Sound
- [ ] Dodati sistem za zvuk
- [ ] Naci zvukove 

## Player
- [ ] Dodati 3 zivota i UI za to
- [ ] Na smrt resetovati i staviti nevidljivost na malo duzi period 
- [ ] Dodati animaciju ili efekat eksplozije kada player umre

## Enemy
- [ ] Stvaranje posle 15-ak sekundi(proizvoljno) / neki tajmer u main-u koji ce inicijalizovati vreme koje treba da istekne da bi se neprijatelj stvorio(Svuda dodati proveru za None)
- [ ] Napravljena je klasa za pickup(collectable) potrebno je dodati da kada se neprijatelj unisti on ispusti pickup koji kada neki od igraca pokupi on dobije jednu BOBMU.
- [ ] Napraviti novi sprite sheet za neprijatelja
- [ ] Dodati animaciju ili efekat ekspolzije kada enemy umre

## Bomba
- [ ] Igrac je dobija kada pokupi pickup, ona trosi vise hp-a od regularnog metka ali na treba na neki poseban nacin da se lansira(npr. ide koso zajedno sa paralaksom ili je teska pa posle kratkog vremena letenja pada)

## Stage
- [ ] Dodati mogucnost igranja igre sa tutorijalima i bez njih, dodati postepeno otezavanje igre(recimo prvih 10-ak sekundi se igraci medjusobno pucaju zatim krece stvaranje projektila sa strane, nakon 10-ak sekunda se stvara neprijatelj...)
- [ ] Tutorijal nivo (ikonama objasniti igracima koje komande treba da se koriste za odredjene akcije, uklopiti uz tok igre)

## Projectiles
- [ ] Popraviti stvaranje projektila, povremeno se desi da se stvori dva projektila na vrlo maloj razlici na z osi sto deluje dosta neprirodno