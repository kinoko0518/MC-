#System->
scoreboard objectives add MCPP.num dummy
#<-System

#hoge - fuga
scoreboard players operation #hoge MCPP.num -= #fuga MCPP.num
#hoge - 1
scoreboard players remove #hoge MCPP.num 1
#hoge * 2
scoreboard players set #test.CONSTANT.2 MCPP.num 2
scoreboard players operation #hoge MCPP.num *= #test.CONSTANT.2 MCPP.num

#System->
scoreboard objectives remove MCPP.num
#<-System