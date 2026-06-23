import pandas as pd, warnings, re, json
warnings.filterwarnings('ignore')

ali = pd.read_csv('支付宝交易明细_20260401-20260621_.csv', encoding='gbk', skiprows=23)
ali.columns=[c.strip() for c in ali.columns]; ali=ali[[c for c in ali.columns if not c.startswith('Unnamed')]]
ali['金额']=pd.to_numeric(ali['金额'],errors='coerce'); ali['dt']=pd.to_datetime(ali['交易时间'],errors='coerce')
wx = pd.read_excel('微信支付账单流水文件_20260401-20260621__20260621204426.xlsx', skiprows=17)
wx.columns=[str(c).strip() for c in wx.columns]
wx['金额(元)']=pd.to_numeric(wx['金额(元)'].astype(str).str.replace('¥','').str.replace(',',''),errors='coerce')
wx['dt']=pd.to_datetime(wx['交易时间'],errors='coerce')
ccb = pd.read_excel('交易明细_8807_20260401_20260621.xls', engine='xlrd', skiprows=5)
ccb.columns=[str(c).strip() for c in ccb.columns]; ccb=ccb.dropna(how='all')
ccb['支出']=pd.to_numeric(ccb['支出'],errors='coerce').fillna(0)
ccb['dt']=pd.to_datetime(ccb['交易日期'].astype(str).str.replace('.0','',regex=False),format='%Y%m%d',errors='coerce')

records=[]
def add(date,acct,cat,amount,note):
    records.append({'date':date.strftime('%Y-%m-%d'),'acct':acct,'cat':cat,'amount':round(float(amount),2),'note':str(note)[:40]})

# ---------- 通用商户自动分类 ----------
def categorize(name, prod):
    s=str(name)+' '+str(prod)
    L=s.lower()
    if re.search(r'餐|饭|食|烧鸟|甜汤|茶|咖啡|酒楼|餐厅|小吃|面|粉|蛋糕|鹅肉|火锅|饺|锅贴|烧烤|鱿鱼|周黑鸭|大米先生|百果园|水产|潘祥记|冰麒麟|饮品|奶茶|食堂|牛肉|甜品|麦当劳|德克士|肯德基|必胜客|汉堡王|塔斯汀|蜜雪|喜茶|瑞幸',s) or re.search(r'coffee|luckin|fantuan|arabica|egg tar|mcdonald|dq\b|linlee|hana-musubi|starbucks|kfc',L): return '餐饮'
    if re.search(r'酒店|民宿|客栈|度假|旅行社|携程|预订',s) or re.search(r'hotel|booking|hostel|resort',L): return '酒店旅游'
    if re.search(r'滴滴|出行|打车|地铁|公交|加油|停车|高铁|机票|的士|租赁|铁路|客运|武铁|旅务通|航空|轮渡',s) or re.search(r'mtr|car rental|uber|lyft',L): return '交通出行'
    if re.search(r'服饰|衣|鞋|优衣|裤|针织',s) or re.search(r'wools|knitwear|wool|uniqlo',L): return '服饰装扮'
    if re.search(r'美发|理发|美容|美甲|推拿|养生|按摩|spa',s): return '美容美发'
    if re.search(r'体育|运动|健身|户外|中体|滑雪|攀',s) or re.search(r'gym|sport',L): return '运动户外'
    if re.search(r'诊所|医院|药店|药房|体检|口腔|牙科|动物医院',s): return '医疗健康'
    if re.search(r'电影|影院|彩票|文化|嬉闹|游乐|景区|祝圣|金顶|鸡足山|遨游|乐园|观星|博物|展览|哔哩哔哩|腾讯视频|爱奇艺|优酷',s) or re.search(r'earth and sky|stargazing|cinema',L): return '文化休闲'
    if re.search(r'话费|宽带|电信|联通|移动|流量|燃气|电费|水费|充值|福昕|迅雷|网盘',s) or re.search(r'todesk|icloud',L) or re.search(r'rogers|netflix|spotify|membership',L): return '充值缴费'
    if re.search(r'超市|便利|百货|盒马|罗森|工艺品|纪念|日用品|黄商|商贸|商行|驿站|哈德逊|水果|药妆',s) or re.search(r'muji|gifts|7-eleven|seven|costco|walmart|mart|京东|淘宝|天猫|拼多多|名创|全棉|purcotton',L): return '日用百货'
    return '其他'

# ---------- 支付宝 ----------
ALI_CAT={'餐饮美食':'餐饮','日用百货':'日用百货','交通出行':'交通出行','文化休闲':'文化休闲','酒店旅游':'酒店旅游',
 '数码电器':'数码电器','保险':'保险','医疗健康':'医疗健康','服饰装扮':'服饰装扮','商业服务':'其他','运动户外':'运动户外',
 '美容美发':'美容美发','母婴亲子':'其他','宠物':'其他','充值缴费':'充值缴费','亲友代付':'亲友代付','其他':'其他'}
a=ali[(ali['收/支']=='支出')&(ali['交易状态']!='交易关闭')].copy()
BIZ=re.compile(r'Lyft|Sporting|Home\s*Depot|得物',re.I)
for _,r in a.iterrows():
    if r['交易分类']=='转账红包': continue
    blob=str(r['交易对方'])+str(r['商品说明'])
    if BIZ.search(blob): continue                                   # 生意支出
    if '洋妈' in str(r['交易对方']): continue                        # 用户:忽略 46879
    if '小红书' in str(r['商品说明']): continue                      # 用户:忽略 20141
    if '闰土' in str(r['交易对方']): continue                        # 用户:忽略 50000
    ac=ALI_CAT.get(r['交易分类'],'其他')
    if ac=='其他':
        c2=categorize(r['交易对方'],r['商品说明'])
        if c2!='其他': ac=c2
    add(r['dt'],'alipay',ac,r['金额'],r['交易对方'])

# ---------- 微信 ----------
GIFT=('Heather','奶奶','爸')
w=wx[(wx['收/支']=='支出')&(~wx['当前状态'].isin(['已全额退款','对方已退还','已退款(¥678.00)']))].copy()
for _,r in w.iterrows():
    name=str(r['交易对方']); amt=r['金额(元)']; t=r['交易类型']
    if '武汉办公家具颜红' in name: continue
    if '武汉-办公设备' in name or '程浩' in name: continue          # 用户:忽略 办公设备5735
    if 'aa鸿斌' in name and abs(amt-3351)<1: continue              # 用户:忽略 04-30 3351
    if t=='转账':
        if 'Gordon' in name and abs(amt-5000)<0.01: add(r['dt'],'wechat','礼物赠与',amt,name); continue
        if any(g in name for g in GIFT): add(r['dt'],'wechat','礼物赠与',amt,name); continue
        c=categorize(name,r['商品'])
        add(r['dt'],'wechat', c if c!='其他' else '个人转账', amt, name); continue
    if '红包' in str(t): add(r['dt'],'wechat','礼物赠与',amt,name); continue
    add(r['dt'],'wechat',categorize(name,r['商品']),amt,name)

# ---------- 建行直接卡 ----------
ccb['渠道']=ccb['交易地点'].astype(str).apply(lambda x:re.split(r'[-－]',str(x))[0] if pd.notna(x) else '')
for _,r in ccb[ccb['支出']>0].iterrows():
    ch=r['渠道']; loc=str(r['交易地点'])
    if re.search(r'支付宝|财付通',ch): continue
    if re.search(r'RCTERYX',loc,re.I): continue
    if r['摘要'] not in ['消费','跨行POS消费']: continue
    if '美团' in ch: cat='餐饮'
    elif '抖音' in ch: cat='日用百货'
    elif '程支付' in ch: cat='酒店旅游'
    else: cat='其他'
    add(r['dt'],'ccb',cat,r['支出'],str(r['对方户名'])[:20])

df=pd.DataFrame(records); df['m']=df['date'].str[:7]
print('总笔数',len(df),' 总额 ¥%.2f ≈ C$%.0f'%(df['amount'].sum(),df['amount'].sum()*0.209))
print('\n=== 全期 按类别 ===')
print(df.groupby('cat')['amount'].agg(['count','sum']).round(0).sort_values('sum',ascending=False).to_string())
print('\n=== 5月 按类别 ===')
m5=df[df['m']=='2026-05']
print(m5.groupby('cat')['amount'].agg(['count','sum']).round(0).sort_values('sum',ascending=False).to_string())
print('\n5月其他剩余明细:')
print(m5[m5['cat']=='其他'].sort_values('amount',ascending=False)[['date','note','amount']].head(12).to_string(index=False))
json.dump(records,open('/home/claude/clean_data.json','w'),ensure_ascii=False)
print('\n写出',len(records),'条')
