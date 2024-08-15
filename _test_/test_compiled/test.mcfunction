#System->
scoreboard objectives add MCPP.num dummy
#<-System

scoreboard players set #test.CONSTANT.2 MCPP.num 2
scoreboard players operation #hoge MCPP.num *= #test.CONSTANT.2 MCPP.num
scoreboard players remove #hoge MCPP.num 1

#System->
scoreboard objectives remove MCPP.num
#<-System