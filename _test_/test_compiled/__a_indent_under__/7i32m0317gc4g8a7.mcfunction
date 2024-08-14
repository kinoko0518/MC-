#hoge * 2
scoreboard players set #test.CONSTANT.2 MCPP.num 2
scoreboard players operation #hoge MCPP.num *= #test.CONSTANT.2 MCPP.num
#hoge - 1
scoreboard players remove #hoge MCPP.num 1
#hoge - fuga
scoreboard players operation #hoge MCPP.num -= #fuga MCPP.num