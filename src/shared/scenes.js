export const SCENES=Object.freeze({
  hall:{name:'烛光礼堂',short:'礼堂',english:'THE GREAT HALL',url:'hall/',line:'还记得，长桌旁的那个位置吗？',description:'穿过石拱与烛光，把脚步放慢一些。'},
  arena:{name:'决斗场',short:'决斗场',english:'DUELING CLUB',url:'arena/',line:'那些并肩作战的日子，仍有回响。',description:'重返看台与场地，看看魔咒留下的光。'},
  potions:{name:'魔药课教室',short:'魔药课',english:'POTIONS CLASSROOM',url:'interior/?scene=potions',line:'坩埚还温着，配方翻到下一页。',description:'沿着石拱走近药柜，找找熟悉的那张课桌。'},
  divination:{name:'占卜课教室',short:'占卜课',english:'DIVINATION CLASSROOM',url:'interior/?scene=divination',line:'帷幔后的微光，藏着未来的答案。',description:'坐进柔软的红色时光，望向桌上的水晶球。'},
  gryffindor:{name:'格兰芬多休息室',short:'格兰芬多',english:'GRYFFINDOR COMMON ROOM',url:'interior/?scene=gryffindor',line:'红金色的勇气，在炉火旁歇一歇。',description:'回到画像、扶手椅与壁炉围成的温暖角落。'},
  slytherin:{name:'斯莱特林休息室',short:'斯莱特林',english:'SLYTHERIN COMMON ROOM',url:'interior/?scene=slytherin',line:'黑湖的绿光，安静地穿过高窗。',description:'沿石拱走进幽绿大厅，看看长桌旁的旧座位。'},
  ravenclaw:{name:'拉文克劳休息室',short:'拉文克劳',english:'RAVENCLAW COMMON ROOM',url:'interior/?scene=ravenclaw',line:'让好奇心，陪我们再看一夜星空。',description:'走过蓝金色星盘，停在天球仪与学院雕像前。'},
  hufflepuff:{name:'赫奇帕奇休息室',short:'赫奇帕奇',english:'HUFFLEPUFF COMMON ROOM',url:'interior/?scene=hufflepuff',line:'植物在窗边长大，朋友在沙发上等你。',description:'推开暖光里的门，让脚步停在圆窗和绿叶之间。'}
});
export const INTERIORS=Object.keys(SCENES).filter(id=>!['hall','arena'].includes(id));
