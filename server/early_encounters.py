"""Explicit provisional first-island encounter reconstruction.

Native resources/skill sets are used. Exact historical random formations and
server stats were not preserved. These entries are not a generic fallback.
"""
ENEMIES={
 'siren':('202001000','2020010','Siren',4500,150),
 'slime':('103011000','1030110','Green Slime',220,20),
 'fish':('103031000','1030310','Sahagin',300,30),
 'mage':('105021000','1050210','Mage',260,80),
 'guard':('105002000','1050020','Goblin Guard',2500,80),
 'dragon':('107001000','1070010','Mini Dragon',850,50),
 'wisp':('108001003','1080010','Blue Wisp',300,60),
 'spider':('109012001','1090120','Black Widow',350,30),
 'skeleton':('112001000','1120010','Skeleton',400,40),
 'shark':('203002000','2030020','Shark',1600,60),
 'zu':('302001000','3020010','Zu',4000,100),
 'abtu':('103021001','1030210','Abtu',320,40),
 'harley':('204001000','2040010',"Hell's Harley",4500,100),
 'darklord':('305011000','3050110','Veritas of the Dark',6500,150),
}
FORMATIONS={
 '1110301':(('bat','slime'),('goblin','spider'),('wisp','bat'),('skeleton','goblin')),
 '1110302':(('spider','bat'),('wisp','slime'),('skeleton','spider'),('guard','goblin')),
 '1110303':(('goblin','spider'),('skeleton','wisp'),('slime','bat'),('guard','goblin','goblin','goblin','goblin')),
 '1110401':(('fish','abtu'),('slime','mage'),('abtu','fish'),('shark',)),
 '1110402':(('mage','slime'),('fish','abtu'),('mage','fish'),('shark','abtu')),
 '1110403':(('abtu','fish'),('mage','slime'),('shark','abtu'),('shark','mage')),
 # Separate native main-route boss after Upper Floors, not the optional
 # higher-rank esper trials (1110405/1110406).
 '1110404':(('siren',),),
 '1110501':(('hornet','goblin'),('dragon',),('nuts','hornet'),('dragon','goblin')),
 '1110502':(('dragon','hornet'),('goblin','nuts'),('dragon','nuts'),('zu',)),
 '1110503':(('hornet','dragon'),('goblin','hornet'),('dragon','nuts'),('zu','hornet')),
 '1110601':(('slime','bat'),('skeleton','wisp'),('spider','slime'),('skeleton','mage')),
 '1110602':(('skeleton','bat'),('slime','spider'),('wisp','skeleton'),('harley',)),
 '1110603':(('slime','skeleton'),('wisp','spider'),('mage','skeleton'),('harley','skeleton')),
 '1110701':(('goblin','guard'),('mage','goblin'),('guard','mage'),('harley',)),
 '1110702':(('guard','mage'),('skeleton','guard'),('mage','mage'),('harley','guard')),
 '1110703':(('guard','goblin'),('mage','guard'),('harley',),('darklord',)),
 '1110801':(('hornet','nuts'),('dragon','goblin'),('spider','hornet'),('zu',)),
 '1110802':(('dragon','hornet'),('nuts','spider'),('zu',),('dragon','dragon')),
 '1110803':(('hornet','dragon'),('spider','nuts'),('dragon','goblin'),('zu','dragon')),
}
