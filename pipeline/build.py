import json
html=open('finance.html',encoding='utf-8').read()
data=json.load(open('clean_data.json',encoding='utf-8'))+json.load(open('cibc_cad.json',encoding='utf-8'))+json.load(open('bmo_cad.json',encoding='utf-8'))
props=json.load(open('props_data.json',encoding='utf-8'))
income=json.load(open('income_data.json',encoding='utf-8'))

# 1) 类别
html=html.replace(
"const CATEGORIES = ['餐饮','购物','居家','水电网','通讯','交通','医疗','教育','娱乐','旅行','保险','人情','订阅','其他'];",
"const CATEGORIES = ['餐饮','日用百货','交通出行','数码电器','服饰装扮','文化休闲','休闲娱乐','酒店旅游','医疗健康','宠物','保险','美容美发','运动户外','充值缴费','房租','亲友代付','礼物赠与','个人转账','其他'];")

# 2) 类别颜色
old_colors='''const CAT_COLORS = {
  '餐饮':'#B14534','购物':'#C9893B','居家':'#7C6A4E','水电网':'#5B8C6E','通讯':'#3E8E9E',
  '交通':'#1C5B57','医疗':'#9C5B6E','教育':'#5C6BA0','娱乐':'#A9803A','旅行':'#3D7B8C',
  '保险':'#6E6962','人情':'#B07A5A','订阅':'#8A7BA8','其他':'#9A958C'
};'''
new_colors='''const CAT_COLORS = {
  '餐饮':'#B14534','日用百货':'#C9893B','交通出行':'#1C5B57','数码电器':'#5C6BA0','服饰装扮':'#9C5B6E',
  '文化休闲':'#A9803A','酒店旅游':'#3D7B8C','医疗健康':'#5B8C6E','保险':'#6E6962','美容美发':'#B07A5A',
  '运动户外':'#3E8E9E','充值缴费':'#7C6A4E','亲友代付':'#8A7BA8','礼物赠与':'#C0667A','个人转账':'#7E8A93','休闲娱乐':'#8C3B3B','宠物':'#B5894A','房租':'#5E8B7E','其他':'#B0AAA0'
};'''
assert old_colors in html, 'colors not found'
html=html.replace(old_colors,new_colors)

# 3) 存储 key 升级,强制载入真实数据
html=html.replace("const KEY = 'ledger:v1';","const KEY = 'ledger:v34';")

# 4) 用真实数据替换 seedDemo
start=html.index('function seedDemo(){')
end_marker='  STATE.properties = props;\n}'
end=html.index(end_marker)+len(end_marker)
real_json=json.dumps(data,ensure_ascii=False,separators=(',',':'))
new_seed='const REAL_PROPS = '+json.dumps(props,ensure_ascii=False)+';\n'+'const REAL_INCOME = '+json.dumps(income,ensure_ascii=False)+';\n'+'const REAL_DATA = '+real_json+''';
function seedDemo(){
  STATE.transactions = REAL_DATA.map(r=>({id:uid(),type:'expense',date:r.date,acct:r.acct,cat:r.cat,amount:r.amount,note:r.note||''}));
  STATE.properties = REAL_PROPS;
  STATE.income = REAL_INCOME;
}'''
html=html[:start]+new_seed+html[end:]

# 5) 顶部加一行数据说明
anchor='  <!-- OVERVIEW -->'
note='''  <div style="background:var(--card);border:1px solid var(--line);border-radius:12px;padding:11px 16px;margin-bottom:18px;font-size:12px;color:var(--ink-soft);line-height:1.6">
    <b style="color:var(--ink)">数据说明：</b>建行中「支付宝/财付通(微信)」渠道扣款已去重 · Arcteryx 公司消费已排除 · 生意支出(Lyft/得物等)·投资·转账·工资未计入 · 支付宝转账红包已排除。加币账户(BMO/CIBC)与不动产待数据补充。
  </div>

'''+anchor
html=html.replace(anchor,note,1)

open('/mnt/user-data/outputs/财务流水看板.html','w',encoding='utf-8').write(html)
print('OK 写出, 体积',len(html),'字符, 嵌入交易',len(data),'条')
