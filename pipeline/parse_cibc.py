import subprocess, re, json
MON={'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
files={'Document_2_.pdf':'4月账单(3/9-4/8)','Document_1_.pdf':'5月账单(4/9-5/8)','Document.pdf':'6月账单(5/9-6/8)'}
amt_re=re.compile(r'(-?[\d,]+\.\d{2})\s*$')
date_re=re.compile(r'^([A-Z][a-z]{2})\s+(\d{1,2})\s+([A-Z][a-z]{2})\s+(\d{1,2})\s+(.*)')

def parse_visa(path):
    txt=subprocess.run(['pdftotext','-layout',path,'-'],capture_output=True,text=True).stdout
    lines=txt.split('\n')
    rows=[]; insec=False
    for ln in lines:
        if 'Your new charges and credits' in ln: insec=True; continue
        if 'Total for 4500' in ln: insec=False; continue
        if not insec: continue
        s=ln.strip()
        m=date_re.match(s)
        if not m: continue
        mon,day,_,_,rest=m.groups()
        am=amt_re.search(rest)
        if not am: continue
        amount=float(am.group(1).replace(',',''))
        desc=rest[:am.start()].strip()
        # 去掉末尾的 Spend Category 词
        desc=re.sub(r'\s{2,}(Foreign Currency Transactions|Retail and Grocery|Transportation|Restaurants|Hotel, Entertainment and Recreation|Home and Office Improvement|Professional and Financial Services|Personal and Household Expenses|Health and Education)\s*$','',desc)
        yr=2026 if MON[mon]<=8 else 2025
        rows.append({'mon':MON[mon],'day':int(day),'date':f'{yr}-{MON[mon]:02d}-{int(day):02d}','desc':desc.strip(),'amount':amount})
    return rows

allrows=[]
for f,label in files.items():
    r=parse_visa(f); 
    for x in r: x['stmt']=label
    allrows+=r
    print(f'{label}: {len(r)} 笔, 合计 ${sum(x["amount"] for x in r):.2f}')
print('总计', len(allrows),'笔')
json.dump(allrows,open('/home/claude/cibc_visa_raw.json','w'),ensure_ascii=False)
# 看看有哪些不同商户(去掉外币明细行已自动跳过)
print('\n--- 抽样:金额≥300 的(便于核对大额) ---')
for x in sorted(allrows,key=lambda r:-r['amount'])[:25]:
    print(f"{x['date']}  ${x['amount']:8.2f}  {x['desc'][:46]}")
