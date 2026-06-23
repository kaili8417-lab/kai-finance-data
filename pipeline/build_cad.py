import json, re
visa=json.load(open('cibc_visa_raw.json'))

def catC(d):
    s=d.lower()
    if re.search(r'intuit|qbooks|home depot|business registry',s): return 'EXCLUDE_BIZ'         # QuickBooks 商业记账
    if re.search(r'bccondosandhomes|epcorenergy',s): return 'FLAG_REALESTATE'  # 待确认
    if re.search(r'overlimit|ez-pay fee|service charge|digidentity|kubra',s): return '其他'
    if re.search(r'sauna|ticketline|academy|banff east|lottery',s): return '文化休闲'
    if re.search(r'gusto|silk road|salmon',s): return '餐饮'
    if re.search(r'mms new york|m&m',s): return '日用百货'
    # 餐饮
    if re.search(r'cafe|coffee|restaurant|ramen|burger|ferg|lemon doodle|king made|rata |king of snake|chicken|hanjan|pho |deville|heytea|starbucks|mcdonald|kfc|tim hortons|coca|four square|salmon|sungiven|boiling point|ichiran|levain|chang|haidilao|joe the juice| spar|ramen-ya|hms host|arabica|machi machi|tarras|caltex fairlie|new world|pak n save|coca-cola|snake|tst-|sq \*ramen|deville|queen of egg|wild|dq|caltex wanaka',s): return '餐饮'
    # 交通
    if re.search(r'airbnb',s): return '酒店旅游'
    if re.search(r'taxi|\bcab\b|cabs|uber| lyft|parking|esso|\bmobil\b|refinery|enterprise|thrifty|avis|cars on booking|air canada|air can|westjet|flair|jetstar|virgin|british awys|cathaypac|air new zeal|flynorse|norse|smarte carte|mtr|tfl |omny|valet|kimber|bagagedepot|skyline cableway|yvr|wilson parking|q.?town airport|street car|london taxi|sumup|inflight|wi-fi onboard|airport paper|hughes',s): return '交通出行'
    # 酒店
    if re.search(r'hotel|marr|intercontinental|kimpton|nh collection|mainport|four points|hermitage|jw |yegjw|happy travels|booking|clocktower|front desk',s): return '酒店旅游'
    # 文化休闲/景点活动
    if re.search(r'skyline|skiline|tourism|watersports|all stars|shotover|viator|tripadvisor|museum|keukenhof|lottery|challenge tekapo|mt cook|inflite|u-fly|cableway|gondola|te anau|alpine centre|sp tarras|four square tekapo|wildrose|ski',s): return '文化休闲'
    # 数码
    if re.search(r'memoryexpress|istore|apple',s): return '数码电器'
    # 服饰
    if re.search(r'annms|leather pocket',s): return '服饰装扮'
    # 医疗(药妆)
    if re.search(r'shoppers drug|drug mart|bcs #|vapo',s): return '医疗健康'
    # 充值缴费/通讯/订阅
    if re.search(r'rogers|telus|shaw|seats.aero|nzeta|australianeta|mobility|epcorenergy|cablesystems',s): return '充值缴费'
    # 日用/超市/便利/免税
    if re.search(r'supermarket|t&t|grocery|duty free|hudson|mktplace|paper plus|wh smith|news travels|hema|enticon|qe home|home depot|business registry|selecta|spar|four square|sungiven|store|shop|mart|foods|seven|vending|elements of nature|smith',s): return '日用百货'
    return '其他'

records=[]; excl=[]; flagged=[]
for v in visa:
    c=catC(v['desc'])
    if c=='EXCLUDE_BIZ': excl.append(v); continue
    if c=='FLAG_REALESTATE': flagged.append(v); continue
    records.append({'date':v['date'],'acct':'cibc','cat':c,'amount':round(v['amount'],2),'note':v['desc'][:40]})

# ---- 支票账户:个人项(手工录入,信用卡还款/投资/转账/存款不计) ----
chq=[
 # 保险 TD INSURANCE
 ('2026-04-06','交通出行',193.21,'TD INSURANCE'),('2026-04-06','交通出行',221.19,'TD INSURANCE'),('2026-04-06','交通出行',9.52,'TD INSURANCE'),
 ('2026-04-14','交通出行',302.36,'TD INSURANCE'),
 ('2026-05-04','交通出行',219.35,'TD INSURANCE'),('2026-05-05','交通出行',221.19,'TD INSURANCE'),('2026-05-05','交通出行',9.52,'TD INSURANCE'),
 ('2026-05-13','交通出行',302.36,'TD INSURANCE'),
 # 水电网
 ('2026-04-13','充值缴费',63.42,'EPCOR'),('2026-04-17','充值缴费',109.20,'SHAW 网络'),
 ('2026-05-14','充值缴费',60.46,'EPCOR'),('2026-05-19','充值缴费',109.20,'SHAW 网络'),
 # 借记卡境外消费(旅行)
 ('2026-05-07','交通出行',62.87,'Deer Park Heights NZ'),('2026-05-11','充值缴费',20.37,'Australia ETA'),('2026-05-21','酒店旅游',641.58,'Hotel(Booking)'),
 # 银行月费
 ('2026-04-30','其他',16.95,'账户月费'),('2026-05-29','其他',16.95,'账户月费'),
 ('2026-04-14','日用百货',1845.00,'yj (EMT 购物)'),
]
for d,c,a,n in chq:
    records.append({'date':d,'acct':'cibc','cat':c,'amount':a,'note':n})

NZ=['wanaka','queenstown','te anau','tekapo','twizel','christchurch','auckland','milford','pukaki','rolleston','timaru','mt cook','mt wellington','new zeal','nz all stars','u-fly','tarras','fairlie','deer park']
for r in records:
    n=r['note'].lower()
    if any(k in n for k in NZ): r['cat']='酒店旅游'
records=[r for r in records if r['date']>='2026-04-01']   # 3月不计,与人民币对齐
json.dump(records,open('cibc_cad.json','w'),ensure_ascii=False)

import pandas as pd
df=pd.DataFrame(records); df['m']=df['date'].str[:7]
print('CIBC 加币消费(已合并信用卡+支票个人项):',len(df),'笔  C$%.2f'%df['amount'].sum())
print('\n=== 按月 ==='); print(df.groupby('m')['amount'].sum().round(2).to_string())
print('\n=== 按类别 ==='); print(df.groupby('cat')['amount'].agg(['count','sum']).round(2).sort_values('sum',ascending=False).to_string())
print('\n=== 已排除(商业-QuickBooks) ==='); print(f'{len(excl)}笔 C${sum(x["amount"] for x in excl):.2f}')
print('=== 待确认 BCCONDOSANDHOMES ===',f'{len(flagged)}笔 C${sum(x["amount"] for x in flagged):.2f}')
print('\n=== 落入"其他"的(待细分) ===')
print(df[df['cat']=='其他'].sort_values('amount',ascending=False)[['date','note','amount']].head(15).to_string(index=False))
