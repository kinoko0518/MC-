#System->
scoreboard objectives add MCPP.num dummy
#<-System

#hoge = 1.1
scoreboard players set #test.MAGNIFICATIONS.hoge num 10
scoreboard players set #test.hoge num 11
#hoge = hoge * 1.1 / 0.01
scoreboard players set #test.CONSTANT.10 MCPP.num 10
scoreboard players operation #test.MAGNIFICATION.hoge MCPP.num *= #test.CONSTANT.10 MCPP.num
scoreboard players operation #hoge MCPP.num *= #test.CONSTANT.10 MCPP.num
scoreboard players set #test.CONSTANT.110 MCPP.num 110
scoreboard players operation #hoge MCPP.num *= ##test.CONSTANT.110 MCPP.num
scoreboard players operation #test.MAGNIFICATION.hoge MCPP.num *= #test.CONSTANT.10 MCPP.num
scoreboard players operation #hoge MCPP.num *= #test.CONSTANT.10 MCPP.num
scoreboard players operation #test.MAGNIFICATION.hoge MCPP.num *= #test.CONSTANT.10 MCPP.num
scoreboard players operation #hoge MCPP.num *= #test.CONSTANT.10 MCPP.num

#System->
scoreboard objectives remove MCPP.num
#<-System