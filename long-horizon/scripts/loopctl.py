#!/usr/bin/env python3
import argparse, json, os, subprocess, sys, hashlib, html
from pathlib import Path
from datetime import datetime, timezone

def now(): return datetime.now(timezone.utc).isoformat()
def load(p, default=None):
    p=Path(p)
    if not p.exists(): return default
    return json.loads(p.read_text())
def save(p,obj):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2)+"\n")
def event(run, kind, data):
    p=Path(run)/'events.jsonl'; p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('a') as f: f.write(json.dumps({'at':now(),'kind':kind,**data})+'\n')
def sha256_path(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def render(run):
    run=Path(run); checklist=load(run/'checklist.json',[]) or []; state=load(run/'run_state.json',{}) or {}
    total=len(checklist); passed=sum(1 for t in checklist if t['status']=='PASS')
    phase_ids=[]
    for t in checklist:
        if t['phase'] not in phase_ids: phase_ids.append(t['phase'])
    phase_rows=[]
    for ph in phase_ids:
        items=[t for t in checklist if t['phase']==ph]; done=sum(1 for t in items if t['status']=='PASS')
        phase_rows.append((ph,done,len(items)))
    hist=[]
    ep=run/'events.jsonl'
    if ep.exists():
        done=0
        for line in ep.read_text().splitlines():
            try: e=json.loads(line)
            except: continue
            if e.get('kind')=='task_status' and e.get('status')=='PASS':
                done += 1; hist.append((e.get('at',''),done))
    width=600; height=120
    pts=[]
    if hist:
        for i,(_,v) in enumerate(hist):
            x=10+(width-20)*(i/max(1,len(hist)-1)); y=height-10-(height-20)*(v/max(1,total)); pts.append(f'{x:.1f},{y:.1f}')
    rows=''.join(f"<tr><td>{html.escape(t['id'])}</td><td>{html.escape(t['phase'])}</td><td>{'☒' if t['status']=='PASS' else '☐'}</td><td>{html.escape(t['title'])}</td><td>{html.escape(t['status'])}</td></tr>" for t in checklist)
    phases=''.join(f'<div class="phase"><b>{html.escape(ph)}</b> {d}/{n}<div class="bar"><span style="width:{(100*d/n if n else 0):.1f}%"></span></div></div>' for ph,d,n in phase_rows)
    poly=f'<polyline points="{" ".join(pts)}" fill="none" stroke="black" stroke-width="2" />' if pts else ''
    doc=f"""<!doctype html><meta charset="utf-8"><title>Long Horizon Progress</title><style>body{{font:13px Tahoma,Arial,sans-serif;background:#c0c0c0;color:#000;margin:12px}}.win{{border:2px outset #fff;background:#ddd}}h1{{font-size:14px;background:#000;color:white;margin:0;padding:5px}}.pad{{padding:8px}}.stat{{display:inline-block;border:2px inset #fff;background:white;padding:5px;margin:2px 4px 8px 0}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{border:1px solid #000;padding:4px;text-align:left}}.phase{{margin:5px 0}}.bar{{height:14px;border:1px solid #000;background:white}}.bar span{{display:block;height:100%;background:#000}}svg{{background:white;border:1px solid #000;max-width:100%;height:auto}}</style><div class="win"><h1>SIGNAL STACK LONG HORIZON — {html.escape(str(state.get('offer','')))}</h1><div class="pad"><div class="stat">State: <b>{html.escape(str(state.get('state','')))}</b></div><div class="stat">Phase: <b>{html.escape(str(state.get('current_phase','')))}</b></div><div class="stat">Progress: <b>{passed}/{total}</b></div>{phases}<h2>Progress over completed boxes</h2><svg viewBox="0 0 {width} {height}" width="{width}" height="{height}">{poly}</svg><h2>Checklist</h2><table><thead><tr><th>ID</th><th>Phase</th><th>Done</th><th>Task</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div></div>"""
    (run/'progress.html').write_text(doc)

def cmd_verify_plan(args):
    d=Path(args.offer_dir); required=['goal.json','phase_plan.json','checklist_seed.json','acceptance_seed.json','external_gates.json']
    missing=[x for x in required if not (d/x).exists()]
    if missing: print(json.dumps({'ok':False,'missing':missing})); return 2
    goal=load(d/'goal.json'); phases=load(d/'phase_plan.json'); tasks=load(d/'checklist_seed.json'); acc=load(d/'acceptance_seed.json')
    phase_ids={p['id'] for p in phases['phases']}; tids=[t['id'] for t in tasks['tasks']]; aids=[a['id'] for a in acc['acceptance']]
    errs=[]
    if len(tids)!=len(set(tids)): errs.append('duplicate task ids')
    if len(aids)!=len(set(aids)): errs.append('duplicate acceptance ids')
    for t in tasks['tasks']:
        if t['phase'] not in phase_ids: errs.append(f"task {t['id']} unknown phase {t['phase']}")
    reqs=set(goal['p0_requirements'])
    covered=set(r for t in tasks['tasks'] for r in t.get('requirement_ids',[]))
    missing_reqs=sorted(reqs-covered)
    if missing_reqs: errs.append('requirements without checklist coverage: '+','.join(missing_reqs))
    print(json.dumps({'ok':not errs,'errors':errs,'phases':len(phase_ids),'tasks':len(tids),'acceptance':len(aids)},indent=2))
    return 0 if not errs else 3

def cmd_init(args):
    od=Path(args.offer_dir); run=Path(args.run_dir); run.mkdir(parents=True,exist_ok=True); (run/'evidence').mkdir(exist_ok=True)
    goal=load(od/'goal.json'); seed=load(od/'checklist_seed.json');
    checklist=[]
    for t in seed['tasks']:
        checklist.append({**t,'status':'PENDING','evidence':[],'updated_at':now()})
    save(run/'checklist.json',checklist); save(run/'acceptance_results.json',{}); save(run/'blockers.json',[])
    ext=load(od/'external_gates.json',{'gates':[]}) or {'gates':[]}
    external=[]
    for g in ext.get('gates',[]): external.append({**g,'status':'UNKNOWN','evidence':None,'updated_at':now()})
    save(run/'external_gates.json',external)
    state={'offer':goal['offer'],'state':'INITIALIZING','current_phase':'P00','started_at':now(),'updated_at':now(),'acceptance_lock_sha256':None,'last_progress_at':now()}
    save(run/'run_state.json',state); (run/'decisions.md').write_text('# Decisions\n\n')
    event(run,'init',{'offer':goal['offer']}); render(run); print(json.dumps(state,indent=2)); return 0

def cmd_compile_acceptance(args):
    seed=load(args.acceptance_seed) or {}
    out={'offer':seed.get('offer'),'compiled_at':now(),'acceptance':[]}
    for a in seed.get('acceptance',[]):
        out['acceptance'].append({'id':a['id'],'phase':a['phase'],'required':a.get('required',True),'description':a.get('description',''),'command':a.get('suggested_command',''),'cwd':'{repo_root}','timeout_sec':900})
    save(args.output,out); print(json.dumps({'output':str(args.output),'acceptance':len(out['acceptance'])},indent=2)); return 0

def cmd_freeze(args):
    run=Path(args.run_dir); lock=Path(args.acceptance_lock)
    if not lock.exists(): print('acceptance lock missing',file=sys.stderr); return 2
    state=load(run/'run_state.json',{}); state['acceptance_lock_sha256']=sha256_path(lock); state['state']='RUNNING'; state['updated_at']=now(); save(run/'run_state.json',state)
    event(run,'acceptance_frozen',{'sha256':state['acceptance_lock_sha256']}); render(run); print(state['acceptance_lock_sha256']); return 0

def cmd_phase(args):
    run=Path(args.run_dir); state=load(run/'run_state.json',{}); state['current_phase']=args.phase; state['updated_at']=now(); save(run/'run_state.json',state); event(run,'phase_start',{'phase':args.phase}); render(run); return 0

def cmd_tick(args):
    run=Path(args.run_dir); arr=load(run/'checklist.json',[]); found=False
    for t in arr:
        if t['id']==args.task_id:
            t['status']=args.status; t['updated_at']=now(); found=True
            if args.evidence: t.setdefault('evidence',[]).append(args.evidence)
            break
    if not found: print('task not found',file=sys.stderr); return 2
    save(run/'checklist.json',arr); state=load(run/'run_state.json',{})
    if args.status=='PASS': state['last_progress_at']=now(); state['updated_at']=now(); save(run/'run_state.json',state)
    event(run,'task_status',{'task_id':args.task_id,'status':args.status,'evidence':args.evidence}); render(run); return 0

def resolve_command(cmd, ctx):
    for k,v in ctx.items(): cmd=cmd.replace('{'+k+'}',str(v))
    return cmd

def cmd_gate(args):
    run=Path(args.run_dir); lock=load(args.acceptance_lock)
    state=load(run/'run_state.json',{}); expected=state.get('acceptance_lock_sha256')
    if expected and sha256_path(args.acceptance_lock)!=expected:
        print('acceptance lock hash mismatch',file=sys.stderr); return 9
    ctx={'offer_slug':args.offer_slug or state.get('offer',''),'repo_root':str(Path(args.repo_root).resolve())}
    results=load(run/'acceptance_results.json',{}) or {}; fail=False; ran=0
    for a in lock.get('acceptance',[]):
        if args.phase and a.get('phase')!=args.phase: continue
        if not a.get('required',True) and not args.include_optional: continue
        ran+=1; cmd=resolve_command(a['command'],ctx); cwd=resolve_command(a.get('cwd','{repo_root}'),ctx)
        log=run/'evidence'/f"acceptance-{a['id']}.log"
        try:
            cp=subprocess.run(cmd,shell=True,cwd=cwd,text=True,capture_output=True,timeout=int(a.get('timeout_sec',900)))
            out=(cp.stdout or '')+'\n--- STDERR ---\n'+(cp.stderr or '')
            log.write_text(out); ok=cp.returncode==0
            results[a['id']]={'phase':a.get('phase'),'command':cmd,'exit_code':cp.returncode,'passed':ok,'at':now(),'log':str(log)}
            if a.get('required',True) and not ok: fail=True
        except Exception as e:
            log.write_text(repr(e)); results[a['id']]={'phase':a.get('phase'),'command':cmd,'exit_code':-1,'passed':False,'at':now(),'log':str(log)}; fail=True
    save(run/'acceptance_results.json',results); event(run,'gate',{'phase':args.phase,'ran':ran,'passed':not fail}); render(run)
    print(json.dumps({'phase':args.phase,'ran':ran,'passed':not fail},indent=2)); return 0 if not fail else 10

def cmd_block(args):
    run=Path(args.run_dir); bs=load(run/'blockers.json',[]) or []; b={'code':args.code,'type':args.type,'message':args.message,'severity':args.severity,'created_at':now(),'resolved_at':None}; bs.append(b); save(run/'blockers.json',bs); event(run,'blocker',b); return 0

def cmd_external(args):
    run=Path(args.run_dir); gates=load(run/'external_gates.json',[]) or []; found=False
    for g in gates:
        if g.get('id')==args.gate_id:
            g['status']=args.status; g['evidence']=args.evidence; g['updated_at']=now(); found=True; break
    if not found: print('external gate not found',file=sys.stderr); return 2
    save(run/'external_gates.json',gates); event(run,'external_gate',{'gate_id':args.gate_id,'status':args.status,'evidence':args.evidence}); render(run); return 0

def cmd_stall(args):
    from datetime import datetime
    run=Path(args.run_dir); state=load(run/'run_state.json',{}); lp=state.get('last_progress_at') or state.get('started_at');
    try: dt=datetime.fromisoformat(lp.replace('Z','+00:00')); age=(datetime.now(timezone.utc)-dt).total_seconds()/60
    except: age=0
    stalled=age>=args.minutes; print(json.dumps({'stalled':stalled,'minutes_since_progress':round(age,1),'threshold':args.minutes},indent=2)); return 20 if stalled else 0

def cmd_status(args):
    run=Path(args.run_dir); state=load(run/'run_state.json',{}); tasks=load(run/'checklist.json',[]) or []; bs=load(run/'blockers.json',[]) or []
    counts={}
    for t in tasks: counts[t['status']]=counts.get(t['status'],0)+1
    out={'state':state,'task_counts':counts,'unresolved_blockers':[b for b in bs if not b.get('resolved_at')]}; print(json.dumps(out,indent=2)); return 0

def cmd_final(args):
    run=Path(args.run_dir); state=load(run/'run_state.json',{}); tasks=load(run/'checklist.json',[]) or []; results=load(run/'acceptance_results.json',{}) or {}; bs=load(run/'blockers.json',[]) or []; gates=load(run/'external_gates.json',[]) or []
    if state.get('acceptance_lock_sha256') and sha256_path(args.acceptance_lock)!=state['acceptance_lock_sha256']:
        print(json.dumps({'complete':False,'reason':'acceptance_lock_hash_mismatch'})); return 9
    required=[a for a in load(args.acceptance_lock).get('acceptance',[]) if a.get('required',True)]
    missing=[a['id'] for a in required if not results.get(a['id'],{}).get('passed')]
    pending=[t['id'] for t in tasks if t['status'] not in ('PASS','DEFERRED')]
    unresolved=[b for b in bs if not b.get('resolved_at')]
    external=[b for b in unresolved if b.get('type')=='EXTERNAL']; internal=[b for b in unresolved if b.get('type')!='EXTERNAL']
    required_external=[g for g in gates if g.get('required_for_complete') and g.get('status')!='GREEN']
    complete=not missing and not pending and not internal and not external and not required_external
    if complete: newstate='COMPLETE'; code=0
    elif not missing and not pending and not internal and (external or required_external): newstate='IMPLEMENTATION_COMPLETE_BLOCKED_EXTERNAL'; code=12
    else: newstate='RUNNING'; code=11
    state['state']=newstate; state['updated_at']=now(); save(run/'run_state.json',state); event(run,'final_check',{'state':newstate,'missing_acceptance':missing,'pending_tasks':pending,'external_blockers':[b['code'] for b in external],'internal_blockers':[b['code'] for b in internal]}); render(run)
    print(json.dumps({'complete':complete,'state':newstate,'missing_acceptance':missing,'pending_tasks':pending,'external_blockers':[b['code'] for b in external],'required_external_gates':[{'id':g.get('id'),'status':g.get('status')} for g in required_external],'internal_blockers':[b['code'] for b in internal]},indent=2)); return code

def build_parser():
    p=argparse.ArgumentParser(); sp=p.add_subparsers(dest='cmd',required=True)
    x=sp.add_parser('verify-plan'); x.add_argument('--offer-dir',required=True); x.set_defaults(func=cmd_verify_plan)
    x=sp.add_parser('init'); x.add_argument('--offer-dir',required=True); x.add_argument('--run-dir',default='.loop'); x.set_defaults(func=cmd_init)
    x=sp.add_parser('compile-acceptance'); x.add_argument('--acceptance-seed',required=True); x.add_argument('--output',default='.loop/acceptance.lock.json'); x.set_defaults(func=cmd_compile_acceptance)
    x=sp.add_parser('freeze'); x.add_argument('--run-dir',default='.loop'); x.add_argument('--acceptance-lock',default='.loop/acceptance.lock.json'); x.set_defaults(func=cmd_freeze)
    x=sp.add_parser('phase'); x.add_argument('--run-dir',default='.loop'); x.add_argument('--phase',required=True); x.set_defaults(func=cmd_phase)
    x=sp.add_parser('tick'); x.add_argument('--run-dir',default='.loop'); x.add_argument('--task-id',required=True); x.add_argument('--status',required=True,choices=['PENDING','IN_PROGRESS','PASS','FAIL','BLOCKED','DEFERRED']); x.add_argument('--evidence'); x.set_defaults(func=cmd_tick)
    x=sp.add_parser('gate'); x.add_argument('--run-dir',default='.loop'); x.add_argument('--acceptance-lock',default='.loop/acceptance.lock.json'); x.add_argument('--phase'); x.add_argument('--repo-root',default='.'); x.add_argument('--offer-slug'); x.add_argument('--include-optional',action='store_true'); x.set_defaults(func=cmd_gate)
    x=sp.add_parser('block'); x.add_argument('--run-dir',default='.loop'); x.add_argument('--code',required=True); x.add_argument('--type',required=True,choices=['EXTERNAL','INTERNAL','HARNESS']); x.add_argument('--message',required=True); x.add_argument('--severity',type=int,default=2); x.set_defaults(func=cmd_block)
    x=sp.add_parser('external'); x.add_argument('--run-dir',default='.loop'); x.add_argument('--gate-id',required=True); x.add_argument('--status',required=True,choices=['UNKNOWN','GREEN','BLOCKED','NOT_REQUIRED']); x.add_argument('--evidence'); x.set_defaults(func=cmd_external)
    x=sp.add_parser('stall'); x.add_argument('--run-dir',default='.loop'); x.add_argument('--minutes',type=int,default=20); x.set_defaults(func=cmd_stall)
    x=sp.add_parser('status'); x.add_argument('--run-dir',default='.loop'); x.set_defaults(func=cmd_status)
    x=sp.add_parser('render'); x.add_argument('--run-dir',default='.loop'); x.set_defaults(func=lambda a:(render(a.run_dir) or 0))
    x=sp.add_parser('final'); x.add_argument('--run-dir',default='.loop'); x.add_argument('--acceptance-lock',default='.loop/acceptance.lock.json'); x.set_defaults(func=cmd_final)
    return p

if __name__=='__main__':
    args=build_parser().parse_args(); sys.exit(args.func(args))
