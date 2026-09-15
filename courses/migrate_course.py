#!/usr/bin/env python3
"""Migrate a legacy course site into the 2026 style. See MIGRATION.md.

Uses the MATH 250 Fall 2024 pages (2026/courses/250/24/) as templates and a
per-course CONFIG. Run from the repo root: python3 2026/courses/migrate_course.py
"""
import re, os, json, html as H

T24 = '2026/courses/250/24/'

def strip_comments(c):
    """Browser-style: <!-- hides everything through the next --> (or to EOF)."""
    out=[];pos=0
    while True:
        i=c.find('<!--',pos)
        if i<0: out.append(c[pos:]); break
        out.append(c[pos:i]); j=c.find('-->',i+4)
        if j<0: break
        pos=j+3
    return ''.join(out)

def balance(chunk):
    out=[];depth=0;pos=0
    for m in re.finditer(r'<div\b[^>]*>|</div>',chunk):
        out.append(chunk[pos:m.start()])
        if m.group(0).startswith('</'):
            if depth>0: depth-=1; out.append(m.group(0))
        else: depth+=1; out.append(m.group(0))
        pos=m.end()
    out.append(chunk[pos:])
    return ''.join(out)+'</div>'*depth

class Migrator:
    def __init__(s, cfg): s.cfg=cfg

    def extract(s, y, f):
        h=open(f"courses/{s.cfg['num']}/{y}/{f}").read()
        c=h[re.search(r'<div class="course_main_?\d*">',h).end():h.find('<div class="footer_wrap">')]
        c=strip_comments(c)
        c=re.sub(r'<div class="notes_section"><span style="color: ?red;[^"]*">This page is for a past course.*?</div>','',c,flags=re.S)
        c=re.sub(r'(\s*(</div>|<p>\s*&nbsp;\s*</p>))+\s*$','',c)
        # legacy indent hack shifts content right without shrinking width -> overflows
        c=c.replace('style="position: relative; left: 40px;','style="margin-left: 40px;')
        return c.strip()

    def rewrite_links(s, c, y):
        sib=s.cfg['siblings']
        def fix(m):
            attr,url=m.group(1),m.group(2)
            if url.startswith(('http','https','#','mailto')): return m.group(0)
            if url.split('#')[0] in sib or url.split('#')[0]=='': return m.group(0)
            if url.startswith('../../../'): return f'{attr}="/{url[9:]}"'
            if url.startswith('../../schedule/'): return f'{attr}="/{url[6:]}"'  # old-site typo for ../../../schedule/
            if url.startswith('../../'): return f'{attr}="/courses/{url[6:]}"'
            return f'{attr}="/courses/{s.cfg["num"]}/{y}/{url}"'
        return re.sub(r'(href|src)="([^"]+)"',fix,c)

    def wrap(s, chunks, xcls=''):
        blocks=[]
        for ch in chunks:
            ch=ch.strip()
            # leading line breaks defeat the :first-child margin rule
            ch=re.sub(r'^(?:\s|<br\s*/?>|&nbsp;)+','',ch)
            # nbsp indentation inside a block-opening heading
            ch=re.sub(r'^(<h\d[^>]*>(?:<span[^>]*>)?)(?:&nbsp;|\s)+', r'\1', ch)
            if not ch or re.fullmatch(r'(\s|<br\s*/?>|&nbsp;)*',ch,re.S): continue
            blocks.append('            <section class="section-block%s">\n                <div class="text-side course-content">\n%s\n                </div>\n            </section>'%(xcls,balance(ch)))
        return '\n\n'.join(blocks)

    def retone(s, tpl):
        c=s.cfg['colors']
        vars_css=(
            'body {\n'
            '            --primary-color: %s;\n'
            '            --course-bright: %s;\n'
            '            --course-faded: %s;\n'
            '            --course-btn: %s;\n'
            '            --nav-hover: %s;\n'
            '            --skip-label-col: %s;\n'
            '            --cal-band: %s;\n'
            '            --cal-class: %s;\n'
            '            --cal-event: %s;\n'
            '            --cal-exam: %s;\n'
            '            --cal-exam-text: %s;\n'
            '            background-color: %s; /* very slight course tint */\n'
            '        }'
        )%(c['dark'],c['bright'],c['faded'],c['btn'],
           c.get('nav_hover','#fff'),c.get('skip_label','#fff'),
           c['cal_band'],c['cal_class'],c.get('cal_event','#eee'),
           c['cal_exam'],c.get('cal_exam_text','#fff'),c['tint'])
        # project pages need their hero-margin overrides kept page-local
        extra=''
        if '<nav class="course-nav project-nav">' in tpl or 'project-heading' in tpl:
            extra=('\n        .hero-section { margin-bottom: 0; }\n'
                   '        .hero-section h1 { margin-bottom: 0; }\n'
                   '        .project-nav { margin: 25px 0; }')
        block=('<link rel="stylesheet" href="../../course.css">\n'
               '    <style>\n        %s%s\n    </style>')%(vars_css,extra)
        tpl=re.sub(r'<style>.*?</style>', block, tpl, count=1, flags=re.S)
        return tpl

    def retone_calendar(s, tpl):
        c=s.cfg['colors']
        tpl=tpl.replace('''<span class="legend-swatch swatch-event" aria-hidden="true"></span> Other date of note''',
            '''<span class="legend-swatch swatch-exam" aria-hidden="true"></span> %s
                        &nbsp;&nbsp;
                        <span class="legend-swatch swatch-event" aria-hidden="true"></span> Other date of note'''%c.get('exam_label','Exam / assessment'))
        tpl=tpl.replace("""        function dayClass(d) {
            if (d.class) return 'class-day';""",
                        """        function dayClass(d) {
            if (d.exam) return 'exam-day';
            if (d.class) return 'class-day';""")
        tpl=tpl.replace("""const label = d.class ? '<span class="sr-only">Class meeting: </span>' :
                                  (d.topic ? '<span class="sr-only">Date of note: </span>' : '');""",
                        """const label = d.exam ? '<span class="sr-only">Exam: </span>' :
                                  d.class ? '<span class="sr-only">Class meeting: </span>' :
                                  (d.topic ? '<span class="sr-only">Date of note: </span>' : '');""")
        tpl=tpl.replace("""const label = d.class ? '<span class="sr-only">Class meeting: </span>' :
                                            '<span class="sr-only">Date of note: </span>';""",
                        """const label = d.exam ? '<span class="sr-only">Exam: </span>' :
                                  d.class ? '<span class="sr-only">Class meeting: </span>' :
                                            '<span class="sr-only">Date of note: </span>';""")
        tpl=tpl.replace('sr-only">Exam: ', 'sr-only">%s: '%c.get('exam_sr','Exam').rstrip(': '))
        return tpl

    def build(s, y, sem, h1, here, content_html, base='syllabus.html', title=None):
        cfg=s.cfg
        tpl=open(T24+base).read()
        tpl=s.retone(tpl)
        if base=='calendar.html': tpl=s.retone_calendar(tpl)
        tpl=tpl.replace('Fall 2024',sem).replace('MATH 250','MATH '+cfg['num'])
        bt=re.search(r'<title>(.*?)</title>',tpl).group(1)
        tpl=tpl.replace('<title>%s</title>'%bt,
                        '<title>%s | Christopher Hanusa</title>'%(title or 'MATH %s %s (%s)'%(cfg['num'],h1,sem)))
        tpl=re.sub(r'<h1>[^<]*</h1>','<h1>%s</h1>'%h1,tpl,count=1)
        rows=[]
        for hh,tt in cfg['subnav'](y):
            cls=' class="here"' if hh==here else ''
            rows.append('                <a href="%s"%s>%s</a>'%(hh,cls,tt))
        tpl=re.sub(r'<nav class="course-nav">.*?</nav>',
                   '<nav class="course-nav">\n'+'\n'.join(rows)+'\n            </nav>',tpl,count=1,flags=re.S)
        lis='\n'.join('                    <li><a href="%s">%s</a></li>'%(hh,tt) for hh,tt in cfg['sidebar'](y))
        tpl=re.sub(r'<ul class="course-links">.*?</ul>',
                   '<ul class="course-links">\n'+lis+'\n                </ul>',tpl,count=1,flags=re.S)
        if content_html is not None:
            i=tpl.find('            <section class="section-block')
            if base=='project.html' and '<nav class="course-nav project-nav">' in tpl:
                i=tpl.find('            <nav class="course-nav project-nav">')
            j=tpl.rfind('</section>',0,tpl.find('</main>'))+len('</section>')
            tpl=tpl[:i]+content_html+tpl[j:]
        return tpl

    def run(s):
        cfg=s.cfg
        for y,sem in cfg['years']:
            outdir='2026/courses/%s/%s/'%(cfg['num'],y); os.makedirs(outdir,exist_ok=True)
            have=set(os.listdir('courses/%s/%s'%(cfg['num'],y)))
            for fname,h1,mode,here in cfg['pages']:
                if isinstance(mode,dict): mode=mode.get(y,mode.get('*'))
                if (y,fname) in cfg.get('exclude',set()): continue
                if fname not in have and fname!='calendar.html': continue
                here = here or fname
                if mode=='calendar':
                    s.gen_calendar(y,sem,outdir); continue
                c=s.rewrite_links(s.extract(y,fname),y)
                if fname!='calendar.html' and re.search(r'<h1\b',c):
                    # content h1s would render at the site's 4em; demote the
                    # hierarchy so h1 sections become block headers
                    c=re.sub(r'<h2\b([^>]*)>',r'<h3\1>',c).replace('</h2>','</h3>')
                    c=re.sub(r'<h1\b([^>]*)>',r'<h2\1>',c).replace('</h1>','</h2>')
                for a,b in cfg.get('content_fixes',{}).get((y,fname),[]):
                    assert a in c, (y,fname,a)
                    c=c.replace(a,b)
                if mode=='index':
                    if cfg.get('index_h3_top'):
                        h2parts=['']  # all headings are top-level; no h2-nested subsections
                        pre=re.split(r'(?=<h[23])',c)
                    else:
                        h2parts=re.split(r'(?=<h2)',c)
                        pre=re.split(r'(?=<h3)',h2parts[0])
                    # before the first h2: split at h3 and upsize (top-level sections)
                    if pre and 'Welcome to' in pre[0] and not pre[0].lstrip().startswith('<h'):
                        pre=pre[1:]
                    pre=[p for p in pre if not (len(p)<400 and
                         re.match(r'Welcome to Math', re.sub(r'<[^>]+>','',p).strip()))]
                    pre=[re.sub(r'<h3\b([^>]*)>',r'<h2\1>',p).replace('</h3>','</h2>') for p in pre]
                    # from the first h2 on: one block per h2, h3s stay as subsections
                    parts=pre+h2parts[1:]
                    out=s.build(y,sem,cfg['name'],'index.html',s.wrap(parts),
                                title='MATH %s: %s (%s)'%(cfg['num'],cfg['name'],sem))
                    out=out.replace('<h1>%s</h1>'%cfg['name'],
                        '<h1>%s</h1>\n                <p>Welcome to Math %s, %s, this %s!</p>'%(cfg['name'],cfg['num'],cfg['name'],sem))
                elif mode=='letters':
                    # short un-headed intro before the first letter moves under the h1
                    hero=''
                    i0=c.find('<div class="course_letter">')
                    if i0>0:
                        pre=c[:i0].strip()
                        if pre and len(pre)<600 and not re.search(r'<h[123]|notes_section',pre):
                            pre=re.sub(r'(?:\s*(?:<br\s*/?>|&nbsp;))+\s*(</center>|</p>)','\\1',pre)
                            hero=re.sub(r'(\s|&nbsp;|<br\s*/?>)+$','',pre); c=c[i0:]
                    pieces=[];last=0
                    for m in re.finditer(r'<div class="course_letter">(.*?)</div>\s*(?=<div class="course_letter">|$)',c,re.S):
                        if c[last:m.start()].strip(): pieces.append(c[last:m.start()])
                        pieces.append(m.group(1)); last=m.end()
                    if c[last:].strip(): pieces.append(c[last:])
                    out=s.build(y,sem,h1,here,s.wrap(pieces,' letter'),base='letters.html')
                    if hero:
                        hero=re.sub(r'</?center>','',hero).strip()
                        out=out.replace('<h1>%s</h1>'%h1,'<h1>%s</h1>\n                <div class="hero-intro">%s</div>'%(h1,hero),1)
                elif mode=='project':
                    c=re.sub(r'<p>\s*&nbsp;\s*</p>','',c)
                    c=re.sub(r'Skip to:\s*(<a href="#\d+">[^<]*</a>\s*(?:&bull;)?\s*)+','',c,count=1)
                    c=re.sub(r'<div class="notes_section"[^>]*>\s*</div>','',c)
                    c=re.sub(r'<a name="\d+"></a>','',c)
                    heads=[]
                    def head(m):
                        heads.append(H.unescape(re.sub(r'<[^>]+>','',m.group(1))).strip())
                        return '<a name="%d"></a>\n                    <h1 class="project-heading">%s</h1>'%(len(heads),heads[-1])
                    c=re.sub(r'<div class="notes_section">\s*(?:<span style="color:#\w{3,6}">)?\s*([^<]{1,60}?)\s*(?:</span>)?\s*</div>',head,c)
                    c=re.sub(r'<span style="color:#\w{3,6}">\s*((?:Project\s*\d+|Portfolio|Final Project)[^<]{0,50}?)\s*</span>',head,c)
                    skip='            <nav class="course-nav project-nav">\n                <span class="skip-label">Skip to:</span>\n'+ \
                         '\n'.join('                <a href="#%d">%s</a>'%(i+1,t.split(':')[0]) for i,t in enumerate(heads))+'\n            </nav>'
                    parts=re.split(r'(?=<a name="\d+"></a>)',c)
                    out=s.build(y,sem,h1,here,skip+'\n\n'+s.wrap(parts),base='project.html')
                else:
                    splitters={'h2':r'(?=<h2)','h23':r'(?=<h[23])','nsec':r'(?=<div class="notes_section"[^>]*>)','single':None}
                    sp=splitters[mode]
                    parts=re.split(sp,c) if sp else [c]
                    hero=''
                    if fname in cfg.get('hero_intro',set()):
                        first=parts[0].strip()
                        if len(parts)>1 and first and len(first)<900 and not re.search(r'<h[123]|notes_section',first):
                            # whole pre-split chunk is a short intro
                            hero=first; parts=parts[1:]
                        else:
                            # peel the leading paragraph run
                            m0=re.match(r'\s*(<p>.*?</p>(\s*<p>.*?</p>)*)',parts[0],re.S)
                            if m0 and len(m0.group(1))<900 and not re.search(r'<h[123]|class="date"|notes_section',m0.group(1)):
                                hero=m0.group(1); parts=[parts[0][m0.end():]]+parts[1:]
                    out=s.build(y,sem,h1,here,s.wrap(parts))
                    if hero:
                        hero=re.sub(r'</?center>','',hero).strip()
                        out=out.replace('<h1>%s</h1>'%h1,'<h1>%s</h1>\n                <div class="hero-intro">%s</div>'%(h1,hero),1)
                open(outdir+fname,'w').write(out)
            print(y,sem,'->',sorted(os.listdir(outdir)))

    def gen_calendar(s, y, sem, outdir):
        cfg=s.cfg; c=cfg['colors']
        h=open('courses/%s/%s/calendar.html'%(cfg['num'],y)).read()
        t=h[h.find('<table'):h.find('</table>')+8]
        weeks=[]
        for r in re.findall(r'<tr[^>]*>(.*?)</tr>',t,re.S)[1:]:
            tds=re.findall(r'<td([^>]*)>(.*?)</td>',r,re.S)
            label=re.sub(r'<[^>]+>|&nbsp;',' ',tds[0][1]).strip()
            days=[]
            for attrs,cell in tds[1:6]:
                m=re.search(r'<sup>(.*?)</sup>',cell,re.S)
                date=re.sub(r'<[^>]+>','',m.group(1)).strip() if m else ''
                topic=re.sub(r'<sup>.*?</sup>','',cell,flags=re.S)
                topic=H.unescape(re.sub(r'<[^>]+>|&nbsp;',' ',topic))
                topic=re.sub(r'\s+',' ',topic).strip()
                d={'date':date}
                if topic: d['topic']=topic
                a=attrs.lower()
                for src in c.get('cal_class_src',[c['cal_class']]):
                    if src.lower() in a: d['class']=True
                if c.get('cal_exam_src') and c['cal_exam_src'].lower() in a: d['exam']=True
                if any(topic.startswith(p) for p in cfg.get('exam_topics',[])): d['exam']=True
                days.append(d)
            note=''
            if len(tds)>6:
                note=H.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>|&nbsp;',' ',tds[6][1]))).strip().replace('-->','').strip()
            w={'week':label,'days':days}
            if note: w['note']=note
            weeks.append(w)
        json.dump({'title':'MATH %s Weekly Schedule'%cfg['num'],'semester':sem,
                   'weekdays':['Mon','Tue','Wed','Thu','Fri'],'weeks':weeks},
                  open(outdir+'calendar.json','w'),indent=1,ensure_ascii=False)
        open(outdir+'calendar.html','w').write(
            s.build(y,sem,'Course Calendar','calendar.html',None,base='calendar.html'))

# ============================== MATH 128 config ==============================
def subnav_128(y):
    items=[('index.html','Home'),('syllabus.html','Syllabus'),('standards.html','Standards')]
    if y!='20': items.append(('letters.html','Letters'))
    items+=[('calendar.html','Calendar'),('project.html','Project'),('notes.html','Content')]
    return items

def sidebar_128(y):
    items=[('syllabus.html','&#128220; Syllabus'),('standards.html','&#127919; Standards')]
    if y!='20': items.append(('letters.html','&#9993;&#65039; Letters from Past Students'))
    items+=[('calendar.html','&#128197; Calendar'),('notes.html','&#128218; Course Content'),
            ('project.html','&#128736;&#65039; Project'),('terms.html','&#128214; Design Terms')]
    if y in ('23','24'): items.append(('makerspace.html','&#128295; The Makerspace'))
    if y=='21': items.append(('https://campuswire.com/c/','&#128172; Campuswire'))
    if y=='23': items.append(('https://discord.com/','&#128172; Discord'))
    return items

CONFIG_128 = {
 'num':'128','name':'Mathematical Design',
 'years':[('20','Fall 2020'),('21','Fall 2021'),('23','Spring 2023'),('24','Spring 2024')],
 'colors':{'dark':'#980','bright':'#CCC422','faded':'#ba4','tint':'#faf9f0','btn':'#760',
           'nav_hover':'#760','skip_label':'#760',
           'cal_band':'#E9E077','cal_class':'#FF6','cal_event':'#DDDDBB',
           'cal_exam':'#980','cal_exam_src':None},
 'exam_topics':['Assess'],
 'subnav':subnav_128,'sidebar':sidebar_128,
 'siblings':{'index.html','syllabus.html','letters.html','calendar.html','project.html',
             'notes.html','standards.html','terms.html','makerspace.html','homework.html'},
 'hero_intro':{'notes.html'},
 'pages':[
   ('index.html','Mathematical Design','index',None),
   ('syllabus.html','Course Syllabus','h2',None),
   ('standards.html','Standards','h2',None),
   ('letters.html','Letters from Past Students','letters',None),
   ('project.html','Course Projects','project',None),
   ('notes.html','Course Content','nsec',None),
   ('terms.html','Design Terms','nsec','index.html'),
   ('makerspace.html','The Makerspace','nsec','index.html'),
   ('calendar.html','Course Calendar','calendar',None),
 ],
}

# ============================== MATH 634 config ==============================
def subnav_634(y):
    if y=='14':
        return [('index.html','Home'),('syllabus.html','Syllabus'),('letters.html','Letters'),
                ('calendar.html','Calendar'),('project.html','Project'),('notes.html','Notes')]
    return [('index.html','Home'),('syllabus.html','Syllabus'),('standards.html','Standards'),
            ('letters.html','Letters'),('project.html','Project'),('notes.html','Content')]

def sidebar_634(y):
    if y=='14':
        return [('syllabus.html','&#128220; Syllabus'),
                ('letters.html','&#9993;&#65039; Letters from Past Students'),
                ('calendar.html','&#128197; Calendar'),
                ('notes.html','&#128218; Notes'),
                ('project.html','&#128736;&#65039; Project'),
                ('guidelines.html','&#128203; Project Guidelines'),
                ('list.html','&#128214; List of Chosen Topics')]
    return [('syllabus.html','&#128220; Syllabus'),('standards.html','&#127919; Standards'),
            ('letters.html','&#9993;&#65039; Letters from Past Students'),
            ('notes.html','&#128218; Course Content'),('project.html','&#128736;&#65039; Project')]

CONFIG_634 = {
 'num':'634','name':'Graph Theory',
 'years':[('14','Spring 2014'),('22','Fall 2022')],
 'colors':{'dark':'#922','bright':'#fbb','faded':'#b55','tint':'#fcf5f5','btn':'#711',
           'nav_hover':'#922','skip_label':'#922',
           'cal_band':'#FCC','cal_class':'#C66','cal_event':'#eee',
           'cal_exam':'#922','cal_exam_src':None},
 'exam_topics':['Exam','Assess'],
 'subnav':subnav_634,'sidebar':sidebar_634,
 'siblings':{'index.html','syllabus.html','letters.html','calendar.html','project.html',
             'notes.html','standards.html','guidelines.html','list.html','homework.html'},
 'hero_intro':{'notes.html'},
 # Fall 2022's calendar/guidelines/list files are stale byte-identical copies of
 # Spring 2014 -- not migrated (letters kept per Chris). F22's only list.html
 # reference sits inside a commented-out project description, so nothing links it.
 'exclude':{('22','calendar.html'),('22','guidelines.html'),('22','list.html')},
 'pages':[
   ('index.html','Graph Theory','index',None),
   ('syllabus.html','Course Syllabus','h2',None),
   ('standards.html','Standards','h2',None),
   ('letters.html','Letters from Past Students','letters',None),
   ('project.html','Course Project','h2',None),
   ('notes.html','Course Content','nsec',None),
   ('guidelines.html','Project Guidelines','single','index.html'),
   ('list.html','List of Chosen Topics','single','project.html'),
   ('calendar.html','Course Calendar','calendar',None),
 ],
}

# ============================== MATH 213 config ==============================
def subnav_213(y):
    items=[('index.html','Home'),('syllabus.html','Syllabus')]
    if y!='15': items.append(('letters.html','Letters'))
    items+=[('calendar.html','Calendar'),('project.html','Projects'),('notes.html','Content')]
    return items

def sidebar_213(y):
    items=[('syllabus.html','&#128220; Syllabus')]
    if y!='15': items.append(('letters.html','&#9993;&#65039; Letters from Past Students'))
    items+=[('calendar.html','&#128197; Calendar'),('notes.html','&#128218; Course Content'),
            ('project.html','&#128736;&#65039; Projects')]
    return items

CONFIG_213 = {
 'num':'213','name':'Math with Mathematica',
 # NOTE: directory number != year for 17 (its pages say Spring 2018)
 'years':[('15','Spring 2015'),('16','Spring 2016'),('17','Spring 2018'),
          ('18','Fall 2018'),('19','Fall 2019')],
 'colors':{'dark':'#A33','bright':'#C66','faded':'#d99','tint':'#faf4f4','btn':'#822',
           'cal_band':'#FCC','cal_class':'#C66','cal_event':'#eee',
           # orange #F96 = project critique days (15-17); black text reads best on it
           'cal_exam':'#F96','cal_exam_src':'#F96','cal_exam_text':'#000',
           'exam_label':'Critique / key date','exam_sr':'Key date'},
 'exam_topics':[],
 'subnav':subnav_213,'sidebar':sidebar_213,
 'siblings':{'index.html','syllabus.html','letters.html','calendar.html','project.html',
             'notes.html','tutorial1.html','project2.html','project3.html'},
 'hero_intro':{'notes.html','tutorial1.html'},
 # 15's project2/3.html are superseded drafts, unlinked on the old site -- skip
 'pages':[
   ('index.html','Math with Mathematica','index',None),
   ('syllabus.html','Course Syllabus','h2',None),
   ('letters.html','Letters from Past Students','letters',None),
   ('project.html','Course Projects','project',None),
   ('notes.html','Course Content','nsec',None),
   ('tutorial1.html','Tutorial 1','h2','notes.html'),
   ('calendar.html','Course Calendar','calendar',None),
 ],
}

# ============================== MATH 141 config ==============================
def subnav_141(y):
    items=[('index.html','Home'),('syllabus.html','Syllabus')]
    if y=='21': items.append(('standards.html','Standards'))
    if y!='14': items.append(('letters.html','Letters'))
    items.append(('calendar.html','Calendar'))
    if y!='14': items.append(('homework.html','Book Problems'))  # F2014's page was never filled in
    items.append(('notes.html','Content' if y=='21' else 'Notes'))
    return items

def sidebar_141(y):
    items=[('syllabus.html','&#128220; Syllabus')]
    if y=='21': items.append(('standards.html','&#127919; Standards'))
    if y!='14': items.append(('letters.html','&#9993;&#65039; Letters from Past Students'))
    items.append(('calendar.html','&#128197; Calendar'))
    if y!='14': items.append(('homework.html','&#128216; Book Problems'))
    items.append(('notes.html','&#128218; Course Content'))
    if y=='21': items.append(('https://campuswire.com/c/','&#128172; Campuswire'))
    return items

CONFIG_141 = {
 'num':'141','name':'Calculus I',
 'years':[('14','Fall 2014'),('15','Spring 2015'),('21','Fall 2021')],
 # palette keyed to the calendar blues: #39C (class days) and #9CE (band)
 'colors':{'dark':'#39C','bright':'#9CE','faded':'#7bd','tint':'#f2f7fb','btn':'#27a',
           'nav_hover':'#069','skip_label':'#069',
           'cal_band':'#9CE','cal_class':'#39C','cal_event':'#eee',
           'cal_exam':'#059','cal_exam_src':'#059'},
 'exam_topics':['Exam','Assess'],
 'subnav':subnav_141,'sidebar':sidebar_141,
 'siblings':{'index.html','syllabus.html','letters.html','calendar.html','notes.html',
             'standards.html','homework.html'},
 'hero_intro':{'notes.html','homework.html'},
 'index_h3_top':True,
 # F2014's homework.html is an unfilled placeholder (all "???") -- not migrated
 'exclude':{('14','homework.html')},
 'pages':[
   ('index.html','Calculus I','index',None),
   ('syllabus.html','Course Syllabus','h2',None),
   ('standards.html','Standards','h2',None),
   ('letters.html','Letters from Past Students','letters',None),
   ('homework.html','Book Problems','single',None),
   ('notes.html','Course Content','nsec',None),
   ('calendar.html','Course Calendar','calendar',None),
 ],
}

# ============================== MATH 142 config ==============================
def subnav_142(y):
    if y=='17':
        return [('index.html','Home'),('syllabus.html','Syllabus'),('standards.html','Standards'),
                ('project.html','Project'),('calendar.html','Calendar'),('notes.html','Daily Topics')]
    return [('index.html','Home'),('letters.html','Letters'),('syllabus.html','Syllabus'),
            ('standards.html','Standards'),('calendar.html','Calendar'),
            ('project.html','Project'),('notes.html','Content')]

def sidebar_142(y):
    items=[('syllabus.html','&#128220; Syllabus'),('standards.html','&#127919; Standards')]
    if y=='20': items.append(('letters.html','&#9993;&#65039; Letters from Past Students'))
    items+=[('calendar.html','&#128197; Calendar'),
            ('project.html','&#128736;&#65039; Project'),
            ('notes.html','&#128218; Course Content')]
    return items

CONFIG_142 = {
 'num':'142','name':'Calculus II',
 'years':[('17','Fall 2017'),('20','Spring 2020')],
 'colors':{'dark':'#079','bright':'#4ad','faded':'#3ab','tint':'#f0f8fa','btn':'#056',
           'nav_hover':'#056','skip_label':'#056',
           'cal_band':'#9CE','cal_class':'#4AD','cal_event':'#eee',
           'cal_exam':'#079','cal_exam_src':None},
 'exam_topics':['Exam','Assess'],
 'subnav':subnav_142,'sidebar':sidebar_142,
 'siblings':{'index.html','syllabus.html','letters.html','calendar.html','notes.html',
             'standards.html','project.html','homework.html'},
 'hero_intro':{'notes.html'},
 'pages':[
   ('index.html','Calculus II','index',None),
   ('syllabus.html','Course Syllabus','h2',None),
   ('standards.html','Standards','h2',None),
   ('letters.html','Letters from Past Students','letters',None),
   ('project.html','Course Project','h2',None),
   ('notes.html','Course Content','nsec',None),
   ('calendar.html','Course Calendar','calendar',None),
 ],
}

# ============================== MATH 201 config ==============================
def subnav_201(y):
    items=[('index.html','Home'),('syllabus.html','Syllabus')]
    if y=='21': items.append(('standards.html','Standards'))
    items+=[('letters.html','Letters'),('calendar.html','Calendar'),
            ('homework.html','Book Problems')]
    if y in ('14s','14f','15'): items.append(('forum.html','Forum'))
    items.append(('notes.html','Content' if y=='21' else 'Notes'))
    return items

def sidebar_201(y):
    items=[('syllabus.html','&#128220; Syllabus')]
    if y=='21': items.append(('standards.html','&#127919; Standards'))
    items+=[('letters.html','&#9993;&#65039; Letters from Past Students'),
            ('calendar.html','&#128197; Calendar'),
            ('homework.html','&#128216; Book Problems')]
    if y in ('14s','14f','15'): items.append(('forum.html','&#128172; Forum'))
    if y=='21': items.append(('assessmentdates.html','&#128198; Assessment Dates'))
    items.append(('notes.html','&#128218; Course Content'))
    if y=='21': items.append(('https://campuswire.com/c','&#128172; Campuswire'))
    return items

CONFIG_201 = {
 'num':'201','name':'Multivariable Calculus',
 'years':[('14s','Spring 2014'),('14f','Fall 2014'),('15','Fall 2015'),
          ('17','Fall 2017'),('21','Spring 2021')],
 'colors':{'dark':'#962','bright':'#fc9','faded':'#b84','tint':'#fdf8f2','btn':'#741',
           'nav_hover':'#962','skip_label':'#962',
           'cal_band':'#FC9','cal_class':'#C73','cal_event':'#eee',
           # yellow #FD5 = exam days; black text reads best on it
           'cal_exam':'#FD5','cal_exam_src':'#FD5','cal_exam_text':'#000'},
 'exam_topics':['Exam','Assess'],
 'subnav':subnav_201,'sidebar':sidebar_201,
 'siblings':{'index.html','syllabus.html','letters.html','calendar.html','notes.html',
             'standards.html','homework.html','forum.html','assessmentdates.html'},
 'hero_intro':{'notes.html','homework.html'},
 'index_h3_top':True,
 'pages':[
   ('index.html','Multivariable Calculus','index',None),
   ('syllabus.html','Course Syllabus','h2',None),
   ('standards.html','Standards','h2',None),
   ('letters.html','Letters from Past Students','letters',None),
   ('homework.html','Book Problems','single',None),
   ('forum.html','Course Forum','single',None),
   ('assessmentdates.html','Assessment Dates','h2','standards.html'),
   ('notes.html','Course Content','nsec',None),
   ('calendar.html','Course Calendar','calendar',None),
 ],
}

# ============================== MATH 245 config ==============================
ERA1_245=('14','15','16')
def subnav_245(y):
    items=[('index.html','Home'),('syllabus.html','Syllabus'),('letters.html','Letters'),
           ('calendar.html','Calendar')]
    if y in ERA1_245:
        items+=[('mathematica.html','Mathematica'),('project.html','Project'),('notes.html','Notes')]
    else:
        items+=[('software.html','Software'),('project.html','Projects'),('notes.html','Content')]
    return items

def sidebar_245(y):
    items=[('syllabus.html','&#128220; Syllabus'),
           ('letters.html','&#9993;&#65039; Letters from Past Students'),
           ('calendar.html','&#128197; Calendar')]
    if y in ERA1_245:
        items+=[('mathematica.html','&#9997;&#65039; Mathematica'),
                ('guidelines.html','&#128203; Project Guidelines'),
                ('project.html','&#128736;&#65039; Project')]
    else:
        items+=[('software.html','&#128187; Software'),
                ('project.html','&#128736;&#65039; Projects')]
    if y in ('21','22'): items.append(('abstracts.html','&#128196; Project Abstracts'))
    items.append(('notes.html','&#128218; Course Content'))
    if y=='21': items.append(('https://campuswire.com/c','&#128172; Campuswire'))
    return items

CONFIG_245 = {
 'num':'245','name':'Mathematical Models',
 # dirs 17=Spring 2018, 19=Fall 2019, 19sp=Spring 2019 (names do not track years)
 'years':[('14','Spring 2014'),('15','Spring 2015'),('16','Spring 2016'),
          ('17','Spring 2018'),('19sp','Spring 2019'),('18','Fall 2018'),
          ('19','Fall 2019'),('20','Spring 2020'),('21','Spring 2021'),('22','Spring 2022')],
 'colors':{'dark':'#629','bright':'#daf','faded':'#96c','tint':'#f8f4fb','btn':'#417',
           'nav_hover':'#629','skip_label':'#629',
           'cal_band':'#daf','cal_class':'#b6e','cal_event':'#eee',
           'cal_class_src':['#b6e','#B070FF'],
           # pink #fbe = exam days in 2014-16; black text
           'cal_exam':'#fbe','cal_exam_src':'#fbe','cal_exam_text':'#000'},
 'exam_topics':['Exam','Assess'],
 'subnav':subnav_245,'sidebar':sidebar_245,
 'siblings':{'index.html','syllabus.html','letters.html','calendar.html','notes.html',
             'project.html','mathematica.html','commands.html','tutorial1.html',
             'guidelines.html','software.html','abstracts.html','notes01.html','notes02.html'},
 'hero_intro':{'notes.html','software.html','notes01.html','notes02.html'},
 'index_h3_top':True,
 'content_fixes':{('19sp','syllabus.html'):[('href="/courses/245/19sp/content.html"','href="notes.html"')]},
 'pages':[
   ('index.html','Mathematical Models','index',None),
   ('syllabus.html','Course Syllabus','h2',None),
   ('letters.html','Letters from Past Students','letters',None),
   ('project.html','Course Projects',{'14':'h2','15':'h2','16':'h2','*':'project'},None),
   ('notes.html','Course Content','nsec',None),
   ('notes01.html','Course Content (Part 1)','nsec','notes.html'),
   ('notes02.html','Course Content (Part 2)','nsec','notes.html'),
   ('mathematica.html','Mathematica','h2',None),
   ('commands.html','Mathematica Commands','h2','mathematica.html'),
   ('tutorial1.html','Tutorial 1','h2','mathematica.html'),
   ('guidelines.html','Project Guidelines','single','index.html'),
   ('software.html','Software','single',None),
   ('abstracts.html','Project Abstracts','letters','project.html'),
   ('calendar.html','Course Calendar','calendar',None),
 ],
}

# ============================== MATH 555 config ==============================
def subnav_555(y):
    return [('index.html','Home'),('syllabus.html','Syllabus'),
            ('calendar.html','Calendar'),('notes.html','Content')]

def sidebar_555(y):
    return [('syllabus.html','&#128220; Syllabus'),('calendar.html','&#128197; Calendar'),
            ('notes.html','&#128218; Course Content')]

CONFIG_555 = {
 'num':'555','name':'Games and Puzzles',
 'years':[('16','Spring 2016')],
 'colors':{'dark':'#087','bright':'#4cb','faded':'#5ba','tint':'#f0faf8','btn':'#065',
           'nav_hover':'#065','skip_label':'#065',
           'cal_band':'#BBF0E0','cal_class':'#6CA','cal_event':'#eee',
           'cal_exam':'#087','cal_exam_src':None},
 'exam_topics':['Exam','Assess'],
 'subnav':subnav_555,'sidebar':sidebar_555,
 'siblings':{'index.html','syllabus.html','calendar.html','notes.html'},
 'hero_intro':{'notes.html'},
 'index_h3_top':True,
 'pages':[
   ('index.html','Games and Puzzles','index',None),
   ('syllabus.html','Course Syllabus','h2',None),
   ('notes.html','Course Content','single',None),
   ('calendar.html','Course Calendar','calendar',None),
 ],
}

# ============================== MATH 250 config (back-ported; 24 is a phantom, untouched) ==============================
def subnav_250(y):
    return [('index.html','Home'),('syllabus.html','Syllabus'),('letters.html','Letters'),
            ('calendar.html','Calendar'),('project.html','Projects'),('notes.html','Content')]

def sidebar_250(y):
    items=[('syllabus.html','&#128220; Syllabus'),
           ('letters.html','&#9993;&#65039; Letters from Past Students'),
           ('calendar.html','&#128197; Calendar'),
           ('notes.html','&#128218; Course Content'),
           ('project.html','&#128736;&#65039; Projects'),
           ('helpfulinfo.html','&#128161; Helpful Info')]
    if y=='20': items.append(('https://campuswire.com/p/G2E499EB3','&#128172; Campuswire'))
    if y=='21': items.append(('https://campuswire.com/p/G6730266B','&#128172; Campuswire'))
    if y=='23': items.append(('https://discord.com/','&#128172; Discord'))
    items.append(('http://wolframcloud.com','&#9729;&#65039; Mathematica Online'))
    return items

CONFIG_250 = {
 'num':'250','name':'Mathematical Computing',
 'years':[('20','Fall 2020'),('21','Fall 2021'),('23','Spring 2023')],
 'colors':{'dark':'#A33','bright':'#C66','faded':'#d99','tint':'#faf4f4','btn':'#822',
           'cal_band':'#FCC','cal_class':'#C66','cal_event':'#eee',
           'cal_exam':'#A33','cal_exam_src':None},
 'exam_topics':['Exam','Assess'],
 'subnav':subnav_250,'sidebar':sidebar_250,
 'siblings':{'index.html','syllabus.html','letters.html','calendar.html','project.html',
             'notes.html','helpfulinfo.html'},
 'hero_intro':{'notes.html'},
 'pages':[
   ('index.html','Mathematical Computing','index',None),
   ('syllabus.html','Course Syllabus','h2',None),
   ('letters.html','Letters from Past Students','letters',None),
   ('project.html','Course Projects','project',None),
   ('notes.html','Course Content','nsec',None),
   ('helpfulinfo.html','Helpful Information','h2','index.html'),
   ('calendar.html','Course Calendar','calendar',None),
 ],
}

# ============================== MATH 636 config (back-ported) ==============================
def subnav_636(y):
    if y in ('14','15'):
        return [('index.html','Home'),('syllabus.html','Syllabus'),('letters.html','Letters'),
                ('calendar.html','Calendar'),('project.html','Project'),('notes.html','Notes')]
    return [('index.html','Home'),('syllabus.html','Syllabus'),('standards.html','Standards'),
            ('letters.html','Letters'),('calendar.html','Calendar'),
            ('project.html','Project'),('notes.html','Content')]

def sidebar_636(y):
    items=[('syllabus.html','&#128220; Syllabus')]
    if y not in ('14','15'): items.append(('standards.html','&#127919; Standards'))
    items+=[('letters.html','&#9993;&#65039; Letters from Past Students'),
            ('calendar.html','&#128197; Calendar'),
            ('notes.html','&#128218; ' + ('Notes' if y in ('14','15') else 'Course Content')),
            ('project.html','&#128736;&#65039; Project')]
    if y in ('14','15','18'): items.append(('guidelines.html','&#128203; Guidelines'))
    return items

CONFIG_636 = {
 'num':'636','name':'Combinatorics',
 'years':[('14','Fall 2014'),('15','Fall 2015'),('18','Fall 2018'),
          ('19','Fall 2019'),('22','Spring 2022')],
 'colors':{'dark':'#093','bright':'#6d7','faded':'#3a6','tint':'#f4faf5','btn':'#062',
           'cal_band':'#9EA','cal_class':'#6C7','cal_event':'#eee',
           'cal_exam':'#283','cal_exam_src':'#283'},
 'exam_topics':['Assess'],
 'subnav':subnav_636,'sidebar':sidebar_636,
 'siblings':{'index.html','syllabus.html','letters.html','calendar.html','project.html',
             'notes.html','standards.html','guidelines.html','homework.html'},
 'hero_intro':{'notes.html'},
 'index_h3_top':True,
 # bare --> typo in the Sp2022 notes source (no matching <!--)
 'content_fixes':{('22','notes.html'):[("/courses/636/22/notes/636sp22ch41c.pdf\">'</a>-->","/courses/636/22/notes/636sp22ch41c.pdf\">'</a>")]},
 'pages':[
   ('index.html','Combinatorics','index',None),
   ('syllabus.html','Course Syllabus','h2',None),
   ('standards.html','Standards','h2',None),
   ('letters.html','Letters from Past Students','letters',None),
   ('project.html','Course Project','h2',None),
   ('notes.html','Course Content','nsec',None),
   ('guidelines.html','Project Guidelines','single','index.html'),
   ('calendar.html','Course Calendar','calendar',None),
 ],
}

CONFIGS={'128':CONFIG_128,'634':CONFIG_634,'213':CONFIG_213,'141':CONFIG_141,'142':CONFIG_142,
         '201':CONFIG_201,'245':CONFIG_245,'555':CONFIG_555,'250':CONFIG_250,'636':CONFIG_636}

if __name__=='__main__':
    import sys
    Migrator(CONFIGS[sys.argv[1] if len(sys.argv)>1 else '128']).run()
