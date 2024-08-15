#System->
scoreboard objectives add MCPP.num dummy
#<-System

#hoge = 1
scoreboard players set #test hoge 1
#hoge = hoge + hoge + hoge
scoreboard players operation #hoge MCPP.num += #hoge MCPP.num
scoreboard players operation #hoge MCPP.num += #hoge MCPP.num

#System->
scoreboard objectives remove MCPP.num
#<-System