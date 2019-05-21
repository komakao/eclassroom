lesson_list = []
lesson_list1 = []

def reset():
    lesson_list.append(['基礎程式設計：使用Scratch 3.X', []])
    lesson_list[0][1].append(['基礎篇', []])
    #--------------------------------名稱-----,檔案下載,編號,官網作品編號, tab, Youtube
    lesson_list[0][1][0][1].append(['教材：貓狗對話', False, 1, 199354464, False, "QLLSbcR8LYc"])
    lesson_list[0][1][0][1].append(['習作：勇者鬥惡龍', False, 2, 199356271, False, False])    
    lesson_list[0][1].append(['計算篇', []])
    lesson_list[0][1][1][1].append(['教材：求平均數', False, 3, 201792802, ["流程圖", "2_1.png"], "kiYf5-WZCY0"])          
    lesson_list[0][1][1][1].append(['教材：成績計算', False, 4, 201793143, ["流程圖", "2_2.png"], False])     
    lesson_list[0][1][1][1].append(['教材：累加計算', False, 5, 201793794, ["流程圖", "2_3.png"], False])    
    lesson_list[0][1][1][1].append(['教材：累乘計算', False, 6, 201794048, ["流程圖", "2_4.png"], False])  
    lesson_list[0][1][1][1].append(['教材：密碼檢查', False, 7, 201794208, ["流程圖", "2_5.png"], False])    
    lesson_list[0][1][1][1].append(['習作：溫度換算', False, 8, 201792945, ["流程圖", "6_1.png"], False])
    lesson_list[0][1][1][1].append(['習作：書店打折', False, 9, 201793454, ["流程圖", "6_2.png"], False])                
    lesson_list[0][1].append(['繪圖篇', []])
    lesson_list[0][1][2][1].append(['教材：畫方形', False, 10, 201791759, False, False])       
    lesson_list[0][1][2][1].append(['教材：擴散方形', False, 11, 201792210, False, False])         
    lesson_list[0][1][2][1].append(['教材：旋轉方形', False, 12, 201792359, False, False])    
    lesson_list[0][1][2][1].append(['習作：畫星星', False, 13, 201791984, False, False])      
    lesson_list[0][1][2][1].append(['習作：放大方形', False, 14, 201792631, False, False])  
    lesson_list[0][1][2][1].append(['習作：平行方形', False, 15, 201792490, False, False])                 
    lesson_list[0][1].append(['遊戲篇', []])
    lesson_list[0][1][3][1].append(['教材：狗狗散步', False, 16, 212207324, ["心智圖", "4_1.png"], False])  
    lesson_list[0][1][3][1].append(['教材：賽馬', False, 17, 212208431, ["心智圖", "4_2.png"], False])  
    lesson_list[0][1][3][1].append(['教材：水族箱', False, 18, 290858812, ["心智圖", "4_3.png"], False])  
    lesson_list[0][1][3][1].append(['教材：大馬路', False, 19, 213986419, ["心智圖", "4_4.png"], False])      
    lesson_list[0][1][3][1].append(['教材：打擊魔鬼', "1_20.zip", 20, 213986594, ["心智圖", "4_5.png"], False])
    lesson_list[0][1][3][1].append(['習作：打地鼠', False, 21, 216179680, ["心智圖", "6_5.png"], False])  
    lesson_list[0][1][3][1].append(['習作：打雷', "1_22.zip", 22, 201575317, ["心智圖", "4_6.png"], False])            
    lesson_list[0][1].append(['模擬篇', []])
    lesson_list[0][1][4][1].append(['教材：電子琴', "1_23.zip", 23, 201575462, False, False])  
    lesson_list[0][1][4][1].append(['教材：電梯', "1_24.zip", 24, 201575481, False, False])
 
    lesson_list1.append(["1",u"第1堂課：Scratch基本介紹",u"範例：綜合應用", 1])
    lesson_list1.append(["2",u"第2堂課：第一個動畫故事",u"範例：第一個動畫", 2])
    lesson_list1.append(["3-1",u"第3堂課：計次式迴圈",u"範例：馬兒跑步", 3])
    lesson_list1.append(["3-2",u"第3堂課：計次式迴圈",u"練習：變大變小", 4])
    lesson_list1.append(["4-1",u"第4堂課：條件式迴圈",u"範例：貓狗賽跑", 5])
    lesson_list1.append(["4-2",u"第4堂課：條件式迴圈",u"練習：發球", 6])
    lesson_list1.append(["5-1",u"第5堂課：無窮迴圈",u"範例：魚兒水中游", 7])
    lesson_list1.append(["5-2",u"第5堂課：無窮迴圈",u"練習：不斷發球", 8])
    lesson_list1.append(["6-1",u"第6堂課：單向選擇結構",u"範例：電流急急棒", 9])
    lesson_list1.append(["6-2",u"第6堂課：單向選擇結構",u"練習：開車", 10])
    lesson_list1.append(["7-1",u"第7堂課：雙向選擇結構",u"範例：打地鼠", 11])
    lesson_list1.append(["7-2",u"第7堂課：雙向選擇結構",u"練習：密碼檢查", 12])
    lesson_list1.append(["8",u"第8堂課：全域變數",u"範例：猴子吃香蕉", 13])
    lesson_list1.append(["9",u"第9堂課：全域變數",u"範例：打魔鬼", 14])
    lesson_list1.append(["10",u"第10堂課：角色變數",u"範例：射蝙蝠", 15])
    lesson_list1.append(["11~12",u"第11~12堂課：角色變數",u"範例：養魚", 16])
    lesson_list1.append(["12",u"第12堂課：角色變數",u"範例：打磚塊",17])
    lesson_list1.append(["A01",u"實戰入門",u"接雞蛋",18])
    lesson_list1.append(["A02",u"實戰入門",u"電流急急棒",19])
    lesson_list1.append(["A03",u"實戰入門",u"打磚塊",20])
    lesson_list1.append(["A04",u"實戰入門",u"打蟑螂",21])
    lesson_list1.append(["A05",u"實戰入門",u"猜數字",22])
    lesson_list1.append(["A06",u"實戰入門",u"射氣球",23])
    lesson_list1.append(["A07",u"實戰入門",u"猴子吃香蕉",24])
    lesson_list1.append(["A08",u"實戰入門",u"聖誕老公公送禮物",25])
    lesson_list1.append(["B01",u"實戰進擊",u"小蜜蜂對抗戰",26])
    lesson_list1.append(["B02",u"實戰進擊",u"貓貓大戰",27])
    lesson_list1.append(["B03",u"實戰進擊",u"夾娃娃",28])
    lesson_list1.append(["B04",u"實戰進擊",u"小章魚快快游",29])
    lesson_list1.append(["B05",u"實戰進擊",u"緊急救援",30])
    lesson_list1.append(["B06",u"實戰進擊",u"大魚吃小魚",31])
    lesson_list1.append(["B07",u"實戰進擊",u"猜拳",32])
    lesson_list1.append(["B08",u"實戰進擊",u"搶救貓咪",33])	
    lesson_list1.append(["C01",u"實戰高手",u"跳遠",34])
    lesson_list1.append(["C02",u"實戰高手",u"對對碰",35])
    lesson_list1.append(["C03",u"實戰高手",u"水果盤",36])
    lesson_list1.append(["C04",u"實戰高手",u"簡易接龍",37])
    lesson_list1.append(["C05",u"實戰高手",u"星際大戰",38])
    lesson_list1.append(["C06",u"實戰高手",u"貪食蛇",39])
    lesson_list1.append(["C07",u"實戰高手",u"九宮拼圖",40])
    lesson_list1.append(["C08",u"實戰高手",u"見縫插針",41])    

reset()

