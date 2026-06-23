import json
def E(i,d,c,a,n): return {'id':f'e{i}','date':d,'cat':c,'amount':round(a,2),'cur':'CAD','note':n}
props=[
 {'id':'p1','name':'10607 73 AVE NW','loc':'House · 自住/翻新','cur':'CAD','exp':[
    E(101,'2026-04-01','房贷/按揭',1388.97,'TD Mortgage'),
    E(102,'2026-05-01','房贷/按揭',1388.97,'TD Mortgage'),
    E(103,'2026-04-06','装修',1826.30,'EPCOR 电费(reno,4-5月平分)'),
    E(104,'2026-05-06','装修',1826.29,'EPCOR 电费(reno,4-5月平分)'),
    E(105,'2026-04-01','地税/房产税',199.63,'Property tax (COE EDMTAXES, BMO)'),
    E(106,'2026-05-01','地税/房产税',199.63,'Property tax (COE EDMTAXES, BMO)'),
 ]},
 {'id':'p2','name':'1202-5051 Imperial Street','loc':'Condo','cur':'CAD','exp':[
    E(201,'2026-04-17','房贷/按揭',3700.00,'RBC Mortgage'),
    E(202,'2026-05-20','房贷/按揭',3700.00,'RBC Mortgage'),
    E(203,'2026-04-01','物业费',549.21,'Condo fee (PROPRTYPAY)'),
    E(204,'2026-05-01','物业费',549.21,'Condo fee (PROPRTYPAY)'),
 ]},
 {'id':'p3','name':'Unit 213-10418 81 Ave','loc':'Condo','cur':'CAD','exp':[
    E(301,'2026-04-01','房贷/按揭',1205.48,'BMO Mortgage'),
    E(302,'2026-05-01','房贷/按揭',1205.48,'BMO Mortgage'),
    E(303,'2026-04-02','物业费',542.43,'Condo fee (PROPRTYPAY)'),
    E(304,'2026-05-04','物业费',542.43,'Condo fee (PROPRTYPAY)'),
 ]},
]
json.dump(props,open('props_data.json','w'),ensure_ascii=False)
for p in props:
    tot=sum(e['amount'] for e in p['exp'])
    print(f"{p['name']}: {len(p['exp'])}笔  C${tot:,.2f}")
print('合计 C$%.2f'%sum(e['amount'] for p in props for e in p['exp']))
