import os, sqlite3, json, re, unicodedata, hmac
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path
ROOT=Path(__file__).parent; DB=os.environ.get('DB_PATH',str(ROOT/'polls.db')); KEY=os.environ.get('ADMIN_KEY','')
OPTIONS=['针对目标市场进行文化适配','与开发人员密切合作，理解上下文内容','保证术语和内容的准确翻译','自然且有沉浸感的语言风格','配音/字幕口型与时长匹配','快速交付，迅速迭代','在多平台与多地区保持一致','其他']
def db():
 c=sqlite3.connect(DB,timeout=15); c.execute('CREATE TABLE IF NOT EXISTS votes(kind TEXT, voter TEXT, value TEXT, PRIMARY KEY(kind,voter))'); return c
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw): super().__init__(*a,directory=str(ROOT/'public'),**kw)
 def reply(self,x,status=200):
  b=json.dumps(x,ensure_ascii=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
 def do_GET(self):
  p=urlparse(self.path).path
  if p=='/api/results':
   with db() as c: rows=c.execute('SELECT kind,value FROM votes').fetchall()
   words={}; scores=[0]*8; n=0; wn=0
   for k,v in rows:
    if k=='word':
     wn+=1
     for w in json.loads(v):
      key=unicodedata.normalize('NFKC',w).casefold(); a=words.setdefault(key,[w,0]); a[1]+=1
    else:
     n+=1
     for i,j in enumerate(json.loads(v)): scores[j]+=8-i
   self.reply({'words':sorted(words.values(),key=lambda a:-a[1]),'wordVoters':wn,'rankVoters':n,'ranking':sorted([{'label':s,'score':scores[i]/n if n else 0,'id':i} for i,s in enumerate(OPTIONS)],key=lambda a:-a['score'])}); return
  super().do_GET()
 def do_POST(self):
  try:
   size=int(self.headers.get('Content-Length','0')); assert 0<size<=1048576; a=json.loads(self.rfile.read(size)); p=urlparse(self.path).path
   if p=='/api/reset':
    if not KEY or not hmac.compare_digest(str(a.get('key','')),KEY): return self.reply({'error':'教师密码错误或未配置'},403)
    k=a.get('kind'); assert k in ('word','rank','all')
    with db() as c: c.execute('DELETE FROM votes' if k=='all' else 'DELETE FROM votes WHERE kind=?',() if k=='all' else (k,))
    return self.reply({'ok':True})
   assert p=='/api/vote'; k=a['kind']; voter=a['voter']; v=a['value']; assert isinstance(voter,str) and re.fullmatch(r'[a-zA-Z0-9-]{16,80}',voter)
   if k=='word':
    assert isinstance(v,list) and len(v)>=1 and all(isinstance(w,str) and 1<=len(w.strip())<=50 for w in v); seen=set(); clean=[]
    for w in v:
     w=unicodedata.normalize('NFKC',w.strip()); key=w.casefold()
     if key not in seen: seen.add(key); clean.append(w)
    v=clean
   else: assert k=='rank' and isinstance(v,list) and len(v)==8 and all(type(j)==int for j in v) and sorted(v)==list(range(8))
   with db() as c: c.execute('INSERT OR REPLACE INTO votes VALUES(?,?,?)',(k,voter,json.dumps(v,ensure_ascii=False)))
   self.reply({'ok':True})
  except (ValueError,KeyError,TypeError,AssertionError): self.reply({'error':'提交格式不正确'},400)
if __name__=='__main__':
 with db(): pass
 ThreadingHTTPServer(('0.0.0.0',int(os.environ.get('PORT','8000'))),H).serve_forever()
