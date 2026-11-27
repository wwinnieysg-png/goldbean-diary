"""Read publicly displayed Hong Kong buyback board prices; fail closed on format changes."""
import json, re, statistics, urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from bs4 import BeautifulSoup
HK = timezone(timedelta(hours=8))
SOURCES = {'kamkau': ('金球珠寶','https://www.kamkau.com/trad/home'), 'taicheong': ('大昌珠寶','https://tcjewellery.co/')}
def text(s): return re.sub(r'\s+', '', s)
def num(s):
    return float(s.replace(',',''))
def pair(s):
    m=re.fullmatch(r'\$?([\d,.]+)每克\$?([\d,.]+)', text(s))
    if not m: raise ValueError('Unexpected price cell')
    return tuple(map(num,m.groups()))
def parse(name, html, now):
    soup=BeautifulSoup(html,'html.parser'); page=soup.get_text(' ',strip=True)
    if name=='kamkau':
        m=re.search(r'更新日期\s*[:：]\s*(\d{4})年(\d{1,2})月(\d{1,2})日\s*(上午|下午)\s*(\d{1,2}):(\d{2})',page)
        if not m: raise ValueError('Missing timestamp')
        y,mo,d,ap,h,mi=m.groups(); stamp=datetime(int(y),int(mo),int(d),int(h)%12+(12 if ap=='下午' else 0),int(mi),tzinfo=HK)
    else:
        m=re.search(r'今日金價更新\s*(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})',page)
        if not m: raise ValueError('Missing timestamp')
        stamp=datetime.fromisoformat('T'.join(m.groups())).replace(tzinfo=HK)
    if stamp.date()!=now.astimezone(HK).date() or stamp>now+timedelta(minutes=5): raise ValueError('Not today / future timestamp')
    found={}
    for table in soup.find_all('table'):
        rows=table.find_all('tr'); header=False
        for row in rows:
            cols=[c.get_text(' ',strip=True) for c in row.find_all(['td','th'],recursive=False)]
            if len(cols)!=3: continue
            if ('賣出' in cols[1] and '買入' in cols[2]): header=True; continue
            if not header: continue
            label=text(cols[0]); kind=None
            if name=='kamkau' and label=='9999金粒(克)': kind='9999'
            elif name=='kamkau' and label=='9999/999金(克)': kind='999_reference'
            elif name=='taicheong' and re.fullmatch(r'999\.9金粒(?:網上有得買→)?',label): kind='9999'
            if not kind: continue
            if name=='kamkau':
                sell,buy=(num(text(c)) for c in cols[1:])
            else:
                sell_t,sell=pair(cols[1]); buy_t,buy=pair(cols[2]);
                if abs(sell_t/37.429-sell)>1.5 or abs(buy_t/37.429-buy)>1.5: raise ValueError('Inconsistent units')
            if not 100<buy<5000 or not buy<=sell<=buy*1.5: raise ValueError('Invalid price')
            entry={'shop':SOURCES[name][0],'url':SOURCES[name][1],'kind':kind,'label':cols[0],'buy':buy,'quotedAt':stamp.isoformat()}
            if kind in found and found[kind]['buy']!=buy: raise ValueError('Conflicting quotes')
            found[kind]=entry
    if '9999' not in found: raise ValueError('No verified pellet price')
    return list(found.values())
def main():
    now=datetime.now(HK); rows=[]; errors={}
    for key,(shop,url) in SOURCES.items():
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'GoldbeanDiary/1.0 (public board price reference)'})
            with urllib.request.urlopen(req,timeout=20) as r: html=r.read(8_000_000).decode('utf-8',errors='replace')
            rows.extend(parse(key,html,now))
        except Exception as e: errors[shop]=str(e)[:200]; print(shop,errors[shop])
    if not any(r['kind']=='9999' for r in rows): raise SystemExit('No valid current gold pellet quotes; previous JSON retained.')
    values=[r['buy'] for r in rows if r['kind']=='9999']
    if max(values)>min(values)*1.08: raise SystemExit('Sources diverge; refusing to update.')
    data={'schema':1,'checkedAt':now.isoformat(),'rows':rows,'errors':errors}
    Path('gold-prices.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__': main()
