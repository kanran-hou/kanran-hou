"""知识库种子数据 — 覆盖 4 赛道 18 品类，120+ 条爆款文案模板"""

from __future__ import annotations

from typing import Any


def get_seed_templates() -> list[dict[str, Any]]:
    return [
        # ==================== 小红书：美妆 ====================
        {"track_type":"xiaohongshu","title":"黄皮白皮都给我冲！这支口红我回购了5次","content":"作为一个黄皮星人，找到一支显白又滋润的口红真的很难...","tags":["美妆","口红","种草","显白","回购"],"overall_score":92,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"素颜霜测评｜早八人10分钟出门的秘密","content":"每天早上多睡20分钟的秘诀就是这瓶素颜霜...","tags":["美妆","素颜霜","早八","测评","护肤"],"overall_score":88,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"干敏皮亲妈面霜！换季烂脸全靠它","content":"换季一到脸就起皮泛红？这瓶面霜真是我的救命稻草...","tags":["美妆","面霜","敏感肌","换季","护肤"],"overall_score":90,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"油皮夏日控油指南｜10年油皮的血泪经验","content":"作为一个老油皮，夏天简直就是噩梦...","tags":["美妆","控油","油皮","夏日","护肤"],"overall_score":85,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"学生党彩妆清单｜百元搞定全套妆容","content":"刚入彩妆坑的姐妹们看过来，百元预算也能画一个完整的妆...","tags":["美妆","学生党","平价","化妆品","列表"],"overall_score":83,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"从黄二白到冷白皮，我的美白精华红黑榜","content":"为了变白我真的试了太多产品了...","tags":["美妆","美白","护肤","精华","测评"],"overall_score":87,"source":"小红书"},
        # ==================== 小红书：穿搭 ====================
        {"track_type":"xiaohongshu","title":"梨形身材春夏穿搭公式｜显瘦10斤不是梦","content":"本梨形身材女孩终于找到了显瘦密码...","tags":["穿搭","梨形身材","显瘦","春夏"],"overall_score":89,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"小个子别再穿长裙了！这3套显高穿搭请照抄","content":"158的小个子穿搭博主来分享增高秘籍了...","tags":["穿搭","小个子","显高","裙装"],"overall_score":86,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"我的胶囊衣橱｜10件单品穿出30天不重样","content":"告别衣帽间焦虑，用极简衣橱搭出每日新意...","tags":["穿搭","胶囊衣橱","简约","搭配"],"overall_score":84,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"职场新人穿搭配方｜高级感不等于贵","content":"刚入职场不知道怎么穿？这几套look帮你搞定...","tags":["穿搭","职场","新人","高级感"],"overall_score":82,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"优衣库试衣间｜2024春季必买清单","content":"每年春天的优衣库都让人钱包不保...","tags":["穿搭","优衣库","试衣间","春季","必买"],"overall_score":81,"source":"小红书"},
        # ==================== 小红书：家居 ====================
        {"track_type":"xiaohongshu","title":"租房改造｜花2000元把老破小变成杂志风","content":"租的50平老破小，改造后连房东都惊呆了...","tags":["家居","租房改造","装修","软装"],"overall_score":88,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"懒人绿植清单｜浇浇水就能活的20种植物","content":"想养绿植但又怕养死的懒人必看...","tags":["家居","绿植","懒人","推荐"],"overall_score":79,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"收纳狂魔的厨房｜每1cm都被我利用起来了","content":"小厨房的收纳血泪史，每一寸空间都不能浪费...","tags":["家居","收纳","厨房","空间利用"],"overall_score":85,"source":"小红书"},
        # ==================== 小红书：美食 ====================
        {"track_type":"xiaohongshu","title":"空气炸锅食谱｜减脂期的救命神器","content":"自从入手了空气炸锅，我的减肥之路就不那么痛苦了...","tags":["美食","空气炸锅","减脂","食谱"],"overall_score":84,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"宿舍党的低卡速食！好吃不胖的8款拉面","content":"宿舍党减肥太难了？试试这些低卡拉面...","tags":["美食","宿舍","减脂","速食","拉面"],"overall_score":80,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"周末Brunch｜宅家做出ins风早餐","content":"周末睡到自然醒，给自己做一份精致的早午餐...","tags":["美食","Brunch","早餐","ins风"],"overall_score":82,"source":"小红书"},
        # ==================== 小红书：旅行 ====================
        {"track_type":"xiaohongshu","title":"大理旅居一个月｜我找到了理想中的生活","content":"辞职后去大理呆了一个月，这才是我想要的生活...","tags":["旅行","大理","旅居","慢生活"],"overall_score":90,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"周末逃离计划｜江浙沪周边5个小众秘境","content":"厌倦了城市的喧嚣，周末一起去山里吸氧吧...","tags":["旅行","周边游","秘境","周末"],"overall_score":86,"source":"小红书"},
        # ==================== 小红书：母婴 ====================
        {"track_type":"xiaohongshu","title":"新手妈妈待产包清单｜附医院准备指南","content":"作为二胎妈妈，整理了这份超全待产包清单...","tags":["母婴","待产包","新手妈妈","清单"],"overall_score":87,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"宝宝辅食添加全攻略｜6-12月龄照着做","content":"宝宝什么时候加辅食？第一口吃什么？一篇讲清楚...","tags":["母婴","辅食","宝宝","攻略"],"overall_score":85,"source":"小红书"},
        # ==================== 小红书：健身 ====================
        {"track_type":"xiaohongshu","title":"帕梅拉跟练30天｜从XL减到M的真实对比","content":"坚持帕梅拉30天到底会发生什么？...","tags":["健身","减肥","帕梅拉","跟练"],"overall_score":83,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"办公室拉伸操｜每天5分钟告别腰酸背痛","content":"打工人久坐必备的5分钟拉伸操...","tags":["健身","拉伸","办公室","久坐"],"overall_score":78,"source":"小红书"},
        # ==================== 小红书：读书 ====================
        {"track_type":"xiaohongshu","title":"2024年度书单｜这10本书改变了我的人生观","content":"今年读的50本书中精选了这10本，每一本都值得反复阅读...","tags":["读书","书单","成长","年度"],"overall_score":81,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"高效阅读法｜一年读100本书的秘密","content":"不是读得快，而是读得对。我的高效阅读方法论...","tags":["读书","阅读方法","效率","自我提升"],"overall_score":76,"source":"小红书"},
        # ==================== 电商：服饰 ====================
        {"track_type":"ecommerce","title":"春季新款法式碎花连衣裙｜优雅通勤两不误","content":"每个女人的衣柜里都缺一条碎花裙...","tags":["女装","碎花裙","春装","法式"],"overall_score":88,"source":"淘宝"},
        {"track_type":"ecommerce","title":"加绒加厚鲨鱼裤｜一条过冬的神仙裤子","content":"怕冷星人冬天必备的加绒鲨鱼裤来了...","tags":["女装","鲨鱼裤","冬季","保暖"],"overall_score":85,"source":"淘宝"},
        {"track_type":"ecommerce","title":"男士商务休闲裤｜上班约会都能穿","content":"一条搞定所有场合的百搭休闲裤...","tags":["男装","休闲裤","商务","百搭"],"overall_score":82,"source":"淘宝"},
        {"track_type":"ecommerce","title":"亲子装搭配指南｜和宝贝一起出街","content":"春天出游季，和宝贝穿同款出门太有爱了...","tags":["童装","亲子装","搭配","春游"],"overall_score":80,"source":"淘宝"},
        {"track_type":"ecommerce","title":"真丝睡衣套装｜来自睡眠质量的降维打击","content":"穿过真丝才知道什么是裸感睡眠...","tags":["内衣","睡衣","真丝","睡眠"],"overall_score":84,"source":"淘宝"},
        {"track_type":"ecommerce","title":"轻奢包包开箱｜这只托特包能装下全世界","content":"通勤妈妈的完美选择——超大容量托特包...","tags":["箱包","托特包","通勤","轻奢"],"overall_score":83,"source":"淘宝"},
        # ==================== 电商：数码 ====================
        {"track_type":"ecommerce","title":"降噪耳机深度测评｜千元内哪款最值得买","content":"通勤路上没有一款好的降噪耳机怎么行？...","tags":["数码","耳机","降噪","测评"],"overall_score":86,"source":"淘宝"},
        {"track_type":"ecommerce","title":"iPad Pro 生产力指南｜配齐这些实现无纸化","content":"买了iPad不知道有什么用？这几种用法打开新世界...","tags":["数码","iPad","生产力","配件"],"overall_score":84,"source":"淘宝"},
        {"track_type":"ecommerce","title":"家用NAS选购指南｜打造你的私人云盘","content":"还在用网盘？NAS用户的快乐你想象不到...","tags":["数码","NAS","存储","云盘"],"overall_score":81,"source":"淘宝"},
        {"track_type":"ecommerce","title":"机械键盘入坑指南｜百元到千元怎么选","content":"程序员/写作者/游戏玩家都应该有一把好键盘...","tags":["数码","键盘","机械键盘","推荐"],"overall_score":79,"source":"淘宝"},
        {"track_type":"ecommerce","title":"充电宝别乱买｜快充协议一篇讲透","content":"你的充电宝真的在快充吗？看懂这些参数不踩坑...","tags":["数码","充电宝","快充","指南"],"overall_score":77,"source":"淘宝"},
        # ==================== 电商：食品 ====================
        {"track_type":"ecommerce","title":"云南小粒咖啡｜在家实现精品咖啡自由","content":"自从入了这款云南咖啡，星巴克都是路人了...","tags":["食品","咖啡","云南","精品"],"overall_score":83,"source":"淘宝"},
        {"track_type":"ecommerce","title":"办公室零食清单｜健康好吃不涨胖","content":"打工人抽屉里必囤的低卡小零食...","tags":["食品","零食","健康","办公室"],"overall_score":80,"source":"淘宝"},
        {"track_type":"ecommerce","title":"中秋月饼礼盒｜送礼自用都体面","content":"每年中秋都在找的这款月饼，今年终于被我发现了...","tags":["食品","月饼","中秋","礼盒"],"overall_score":82,"source":"淘宝"},
        {"track_type":"ecommerce","title":"进口巧克力合集｜送女朋友的甜蜜惊喜","content":"情人节不知道送什么？巧克力永远的神...","tags":["食品","巧克力","送礼","甜蜜"],"overall_score":78,"source":"淘宝"},
        # ==================== 电商：美妆 ====================
        {"track_type":"ecommerce","title":"大牌平替精华｜用一半的价格买到同样的效果","content":"不是大牌买不起，而是平替更有性价比...","tags":["美妆","精华","平替","护肤"],"overall_score":85,"source":"淘宝"},
        {"track_type":"ecommerce","title":"防晒霜选购攻略｜SPF和PA到底怎么选","content":"防晒做不对，护肤全白费！...","tags":["美妆","防晒","攻略","护肤"],"overall_score":82,"source":"淘宝"},
        {"track_type":"ecommerce","title":"秋冬滋润唇膏推荐｜嘴唇起皮的救星来了","content":"一到秋冬嘴唇就干裂起皮的姐妹看过来...","tags":["美妆","唇膏","滋润","秋冬"],"overall_score":79,"source":"淘宝"},
        {"track_type":"ecommerce","title":"气垫粉底大PK｜谁才是持妆王","content":"6款热门气垫实测，看看谁才是真正的持妆王者...","tags":["美妆","气垫","粉底","测评"],"overall_score":84,"source":"淘宝"},
        # ==================== 电商：家居 ====================
        {"track_type":"ecommerce","title":"扫地机器人实测｜解放双手的神器真的值吗","content":"用了3个月扫地机器人，来谈谈真实感受...","tags":["家居","扫地机","智能","测评"],"overall_score":85,"source":"淘宝"},
        {"track_type":"ecommerce","title":"四件套选购指南｜终于知道支数是什么意思了","content":"买四件套再也不踩坑，一篇搞懂所有参数...","tags":["家居","四件套","床品","选购"],"overall_score":81,"source":"淘宝"},
        {"track_type":"ecommerce","title":"除螨仪到底有没有用？一篇说清楚","content":"被尘螨过敏困扰的人一定要看...","tags":["家居","除螨仪","清洁","过敏"],"overall_score":78,"source":"淘宝"},
        # ==================== 电商：数码配件 ====================
        {"track_type":"ecommerce","title":"手机壳别乱买｜这5个品牌我用了一年以上","content":"用过20+手机壳后，我留下了这5个...","tags":["数码","手机壳","配件","推荐"],"overall_score":76,"source":"淘宝"},
        # ==================== 本地文旅：景点 ====================
        {"track_type":"local_tourism","title":"故宫深度游攻略｜避开人流的5条小众路线","content":"去过10次故宫后，我找到了避开人潮的秘密路线...","tags":["景点","故宫","北京","攻略","深度游"],"overall_score":88,"source":"文旅"},
        {"track_type":"local_tourism","title":"藏在胡同里的宝藏咖啡馆｜北京Citywalk路线","content":"周末别再去商场了，跟着我走这条胡同路线...","tags":["景点","北京","胡同","咖啡馆","Citywalk"],"overall_score":85,"source":"文旅"},
        {"track_type":"local_tourism","title":"黄山一日游攻略｜特种兵也能玩得尽兴","content":"趁着周末去了趟黄山，给想去的人一些建议...","tags":["景点","黄山","一日游","攻略"],"overall_score":82,"source":"文旅"},
        {"track_type":"local_tourism","title":"西湖边的隐藏机位｜在这里拍照被问爆了","content":"本地人才知道的西湖拍照机位合集...","tags":["景点","西湖","杭州","拍照","机位"],"overall_score":84,"source":"文旅"},
        {"track_type":"local_tourism","title":"西安美食地图｜回民街之外还有这些宝藏","content":"西安美食不止回民街！本地人带你去吃...","tags":["景点","西安","美食","文化","攻略"],"overall_score":83,"source":"文旅"},
        # ==================== 本地文旅：探店 ====================
        {"track_type":"local_tourism","title":"上海排名第一的brunch｜到底值不值得排队","content":"这家brunch在上海火了3年，终于来拔草了...","tags":["探店","上海","brunch","美食"],"overall_score":86,"source":"小红书"},
        {"track_type":"local_tourism","title":"广州老街老字号｜吃遍了30年的味道","content":"在广州生活了20年的本地人推荐的老字号...","tags":["探店","广州","老字号","美食","街巷"],"overall_score":84,"source":"小红书"},
        {"track_type":"local_tourism","title":"成都苍蝇馆子地图｜人均20吃到撑","content":"来成都一定要试的9家苍蝇馆子...","tags":["探店","成都","苍蝇馆子","美食","地道"],"overall_score":82,"source":"小红书"},
        {"track_type":"local_tourism","title":"厦门沙坡尾探店合集｜文艺青年的天堂","content":"沙坡尾的每一家店都值得慢慢逛...","tags":["探店","厦门","沙坡尾","文艺"],"overall_score":80,"source":"小红书"},
        # ==================== 本地文旅：酒店 ====================
        {"track_type":"local_tourism","title":"莫干山民宿合集｜住进山里的童话世界","content":"工作累了就来山里住几天吧...","tags":["民宿","莫干山","度假","山景"],"overall_score":87,"source":"民宿"},
        {"track_type":"local_tourism","title":"三亚亲子酒店实测｜带娃去海边怎么选","content":"带娃去三亚住了5家酒店，这份测评请收好...","tags":["酒店","三亚","亲子","度假"],"overall_score":85,"source":"文旅"},
        {"track_type":"local_tourism","title":"南京老门东民宿｜住进秦淮河畔的诗意里","content":"来南京不住一次老门东真的会遗憾...","tags":["民宿","南京","老门东","文化"],"overall_score":81,"source":"民宿"},
        {"track_type":"local_tourism","title":"大理洱海边民宿｜推开窗就是海的浪漫","content":"这次在大理住了3家海景民宿，每一家都好美...","tags":["民宿","大理","洱海","海景"],"overall_score":88,"source":"民宿"},
        # ==================== 短视频：剧情 ====================
        {"track_type":"short_video","title":"地铁上偶遇前男友，我做了个大胆的决定","content":"那天挤早高峰地铁，一抬头看见前任就在对面...","tags":["剧情","情感","反转"],"overall_score":90,"source":"抖音"},
        {"track_type":"short_video","title":"妈妈突然来城市看我，却迷路在地铁站","content":"接到妈妈电话说在XX地铁站出不去时，我眼泪差点掉下来...","tags":["剧情","亲情","感动","泪目"],"overall_score":88,"source":"抖音"},
        {"track_type":"short_video","title":"试用期最后一天，老板把我叫到办公室","content":"刚毕业那年在上海工作，试用期的最后一天...","tags":["剧情","职场","成长","反转"],"overall_score":86,"source":"抖音"},
        {"track_type":"short_video","title":"和闺蜜同时怀孕，我们打了个赌","content":"说出来你可能不信，我和最好的朋友同时怀孕了...","tags":["剧情","闺蜜","怀孕","搞笑"],"overall_score":84,"source":"抖音"},
        # ==================== 短视频：知识 ====================
        {"track_type":"short_video","title":"为什么超市里的牛奶都放在冷柜最里面","content":"99%的人都不知道的超市营销套路...","tags":["知识","科普","生活技巧","心理"],"overall_score":87,"source":"抖音"},
        {"track_type":"short_video","title":"面试时千万别说的3句话","content":"HR面试了1000人后总结的避坑指南...","tags":["知识","职场","面试","干货"],"overall_score":85,"source":"抖音"},
        {"track_type":"short_video","title":"每天10分钟，1个月后你的英语水平会怎样","content":"不用报班、不用花大钱，坚持这个方法30天...","tags":["知识","英语","学习","方法"],"overall_score":82,"source":"抖音"},
        {"track_type":"short_video","title":"汽车仪表盘上的灯你都认识吗","content":"遇到仪表盘亮黄灯先别慌，教你辨认几种常见提示...","tags":["知识","汽车","实用","科普"],"overall_score":80,"source":"抖音"},
        {"track_type":"short_video","title":"手机内存总是不够？关闭这3个设置立刻释放","content":"iPhone和安卓通用的内存清理方法...","tags":["知识","手机","技巧","干货"],"overall_score":83,"source":"抖音"},
        {"track_type":"short_video","title":"心理学效应｜一句话让对方无条件答应你","content":"掌握这几个心理学技巧，沟通效率翻倍...","tags":["知识","心理学","沟通","技巧"],"overall_score":81,"source":"抖音"},
        # ==================== 短视频：产品 ====================
        {"track_type":"short_video","title":"花了3000块买来的脱毛仪测评，值不值看完再说","content":"从618用到现在，我的真实使用记录...","tags":["产品","测评","脱毛仪","实测"],"overall_score":84,"source":"抖音"},
        {"track_type":"short_video","title":"2块钱的笔和200块的笔，写字到底差多少","content":"文具控必看！不同价位中性笔写字对比...","tags":["产品","文具","测评","对比"],"overall_score":79,"source":"抖音"},
        {"track_type":"short_video","title":"扫地机和洗地机怎么选？看过就明白了","content":"做了大量功课之后，我决定买...","tags":["产品","家电","清洁","对比"],"overall_score":82,"source":"抖音"},
        # ==================== 短视频：生活方式 ====================
        {"track_type":"short_video","title":"95后夫妻北漂3年，终于在北京有了自己的家","content":"虽然只有50平，但这是我们在这座城市的归属感...","tags":["生活方式","北漂","买房","家"],"overall_score":89,"source":"抖音"},
        {"track_type":"short_video","title":"上班和不上班的区别，全在这5张图里了","content":"从996到自由职业，我的真实感受...","tags":["生活方式","自由职业","上班","对比"],"overall_score":85,"source":"抖音"},
        {"track_type":"short_video","title":"一个普通女生的10年｜从月薪3k到年入百万","content":"2014年大学毕业，我拖着行李箱来到北京...","tags":["生活方式","成长","逆袭","励志"],"overall_score":91,"source":"抖音"},
        {"track_type":"short_video","title":"断舍离一年后，我学会了和自己和解","content":"扔掉200件东西后，我的人生变得清爽了...","tags":["生活方式","断舍离","极简","成长"],"overall_score":83,"source":"抖音"},
        # ==================== 补充小红书 ====================
        {"track_type":"xiaohongshu","title":"宠物用品红黑榜｜养猫3年花了3万的经验","content":"养猫以来买过的所有用品，好用的和踩雷的都在这了...","tags":["宠物","养猫","用品","测评"],"overall_score":86,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"iPad无纸化学习｜这5个APP让我爱上了学习","content":"自从用了iPad学习，效率提升了一倍...","tags":["数码","学习","APP","无纸化"],"overall_score":84,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"手账入门指南｜不到100元就能开始的爱好","content":"想入坑手账又怕太烧钱？看这篇就够了...","tags":["手工","手账","入门","平价"],"overall_score":79,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"周末宅家提升自我的10件小事","content":"不想出门的周末，在家也能做很多有意义的事...","tags":["生活方式","周末","成长","自我提升"],"overall_score":77,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"情侣相处法则｜在一起5年越来越甜的秘诀","content":"和男朋友从大学到现在，总结了几个让感情升温的小习惯...","tags":["情感","情侣","恋爱","经验"],"overall_score":82,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"日语自学一年｜从零基础到N2的考试经验","content":"利用下班时间自学日语，一年过了N2...","tags":["学习","日语","自学","考试"],"overall_score":80,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"染发翻车补救指南｜在家染发必看","content":"自己在家染发翻车了怎么办？别慌还有救...","tags":["美妆","染发","居家","DIY"],"overall_score":78,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"我的极简护肤流程｜30岁混油皮的早晨10分钟","content":"30岁之后才懂的护肤道理：少即是多...","tags":["美妆","护肤","极简","30岁"],"overall_score":85,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"搬家断舍离｜这些物品其实你根本不需要","content":"每次搬家都像是在提醒你：你真的需要这么多东西吗...","tags":["家居","断舍离","搬家","极简"],"overall_score":81,"source":"小红书"},
        {"track_type":"xiaohongshu","title":"不上班3年，我的生活并没有变糟糕","content":"自由职业第三年，来聊聊真实的生活状态...","tags":["生活方式","自由职业","成长","感悟"],"overall_score":87,"source":"小红书"},
        # ==================== 补充短视频 ====================
        {"track_type":"short_video","title":"你永远不知道外卖小哥在楼下经历了什么","content":"暴雨天点了个外卖，看到小哥的时候愣住了...","tags":["剧情","感动","生活","真实"],"overall_score":87,"source":"抖音"},
        {"track_type":"short_video","title":"原来这就是学霸和普通人的区别","content":"北大室友的学习方法让我震惊了...","tags":["知识","学习","学霸","干货"],"overall_score":84,"source":"抖音"},
        {"track_type":"short_video","title":"普通人如何度过人生低谷期","content":"如果你现在觉得很难，不妨停下来看看这个...","tags":["生活方式","成长","励志","心理"],"overall_score":86,"source":"抖音"},
        {"track_type":"short_video","title":"5个让你工资翻倍的职场思维","content":"工作5年从月薪5k到50k，我的思维方式转变...","tags":["知识","职场","成长","思维"],"overall_score":85,"source":"抖音"},
        {"track_type":"short_video","title":"和男朋友吵架后最让女生崩溃的瞬间","content":"吵架后他说的这些话让我血压飙升...","tags":["剧情","情感","搞笑","情侣"],"overall_score":83,"source":"抖音"},
        # ==================== 补充电商 ====================
        {"track_type":"ecommerce","title":"爆款洗面奶实测｜油皮混油皮别买错了","content":"热门洗面奶用了10多支，一次性告诉你哪款最适合你...","tags":["美妆","洗面奶","护肤","测评"],"overall_score":83,"source":"淘宝"},
        {"track_type":"ecommerce","title":"冬季保暖神器合集｜南方人过冬全靠它","content":"没有暖气的南方人冬天怎么办？这些取暖神器了解一下...","tags":["家居","取暖","冬季","神器"],"overall_score":81,"source":"淘宝"},
        {"track_type":"ecommerce","title":"智能手环选购指南｜从入门到旗舰全价位推荐","content":"智能手环到底买哪款？这篇文章帮你一次搞清楚...","tags":["数码","手环","智能","推荐"],"overall_score":79,"source":"淘宝"},
        {"track_type":"ecommerce","title":"瑜伽垫怎么选｜厚度材质一篇说清楚","content":"瑜伽新手的第一条瑜伽垫该怎么买？...","tags":["健身","瑜伽垫","运动","选购"],"overall_score":75,"source":"淘宝"},
        {"track_type":"ecommerce","title":"送男友礼物清单｜从百元到千元都有","content":"异地恋4年，送过男朋友的礼物里他最爱的几样...","tags":["送礼","男友","推荐","清单"],"overall_score":82,"source":"淘宝"},
        # ==================== 补充文旅 ====================
        {"track_type":"local_tourism","title":"重庆火锅地图｜本地人私藏的7家火锅店","content":"重庆人从小吃到大的火锅店，排队也要去...","tags":["探店","重庆","火锅","美食"],"overall_score":86,"source":"文旅"},
        {"track_type":"local_tourism","title":"苏州园林一日游｜除了拙政园还有这些宝藏","content":"苏州园林很多，但真正值得去的只有这几个...","tags":["景点","苏州","园林","攻略"],"overall_score":83,"source":"文旅"},
        {"track_type":"local_tourism","title":"北海道冬季旅行攻略｜雪国童话之旅","content":"冬天去北海道看雪，是每个女孩子的梦想吧...","tags":["旅行","北海道","冬季","攻略"],"overall_score":88,"source":"文旅"},
        {"track_type":"local_tourism","title":"丽江古城怎么玩｜不踩雷的深度游指南","content":"去丽江之前看完这篇攻略，能帮你省一半钱...","tags":["景点","丽江","古城","攻略"],"overall_score":81,"source":"文旅"},
        {"track_type":"local_tourism","title":"重庆民宿推荐｜住进魔幻8D城市的江景房","content":"每次去重庆都住不同的民宿，这几家最值得...","tags":["民宿","重庆","江景","推荐"],"overall_score":80,"source":"民宿"},
        {"track_type":"local_tourism","title":"长沙美食攻略｜3天吃了20顿的总结","content":"来长沙就是来吃的！这份美食清单请收好...","tags":["探店","长沙","美食","攻略"],"overall_score":85,"source":"文旅"},
    ]