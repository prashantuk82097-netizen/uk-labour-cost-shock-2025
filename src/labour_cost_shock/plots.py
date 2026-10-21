from __future__ import annotations
from pathlib import Path
from html import escape
import pandas as pd


def _write_svg(out: Path, width: int, height: int, body: str, title: str) -> None:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<title>{escape(title)}</title>
<style>
text {{ font-family: Arial, Helvetica, sans-serif; fill: #1f2937; }}
.title {{ font-size: 20px; font-weight: 700; }}
.label {{ font-size: 12px; }}
.small {{ font-size: 10px; fill: #4b5563; }}
.axis {{ stroke: #6b7280; stroke-width: 1; }}
.grid {{ stroke: #e5e7eb; stroke-width: 1; }}
</style>
<rect width="100%" height="100%" fill="white"/>
{body}
</svg>'''
    out.write_text(svg, encoding="utf-8")


def lcei_ranking(lcei: pd.DataFrame, out: Path):
    d = lcei.sort_values("final_LCEI").reset_index(drop=True)
    width, height = 1000, 650
    left, right, top, bottom = 330, 55, 60, 55
    plot_w = width-left-right; plot_h = height-top-bottom
    lo = min(-1.6, float(d["final_LCEI"].min())-0.1); hi = max(2.6, float(d["final_LCEI"].max())+0.1)
    x = lambda v: left + (float(v)-lo)/(hi-lo)*plot_w
    row_h = plot_h/len(d)
    zero = x(0)
    parts=[f'<text x="{width/2}" y="28" text-anchor="middle" class="title">Pre-policy Labour-Cost Exposure Index by SIC section</text>',
           f'<line x1="{zero:.1f}" y1="{top}" x2="{zero:.1f}" y2="{top+plot_h}" class="axis"/>']
    for tick in [-1,0,1,2]:
        if lo<=tick<=hi:
            xx=x(tick); parts.append(f'<line x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{top+plot_h}" class="grid"/>')
            parts.append(f'<text x="{xx:.1f}" y="{height-25}" text-anchor="middle" class="small">{tick}</text>')
    for i,r in d.iterrows():
        cy=top+(i+0.5)*row_h; val=float(r.final_LCEI); xv=x(val)
        bx=min(zero,xv); bw=abs(xv-zero)
        parts.append(f'<rect x="{bx:.1f}" y="{cy-row_h*0.32:.1f}" width="{bw:.1f}" height="{row_h*0.64:.1f}" fill="#4e79a7"/>')
        label=f'{r.sic_section} — {r.sector}'
        parts.append(f'<text x="{left-10}" y="{cy+4:.1f}" text-anchor="end" class="label">{escape(label)}</text>')
        anchor='start' if val>=0 else 'end'; tx=xv+(5 if val>=0 else -5)
        parts.append(f'<text x="{tx:.1f}" y="{cy+4:.1f}" text-anchor="{anchor}" class="small">{val:.2f}</text>')
    parts.append(f'<text x="{left+plot_w/2}" y="{height-5}" text-anchor="middle" class="label">Final LCEI (standardised composite)</text>')
    _write_svg(Path(out),width,height,'\n'.join(parts),'Pre-policy Labour-Cost Exposure Index by SIC section')


def quartile_trends(panel: pd.DataFrame, out: Path):
    sectors=panel[["sector","final_LCEI"]].drop_duplicates().sort_values("final_LCEI").reset_index(drop=True)
    sectors["quartile"]=pd.qcut(sectors["final_LCEI"],4,labels=["Q1 lowest","Q2","Q3","Q4 highest"])
    d=panel.merge(sectors[["sector","quartile"]],on="sector",how="left")
    g=d.groupby(["date","quartile"],observed=True)["employment_index_mar2025_100"].mean().reset_index()
    width,height=1000,520; left,right,top,bottom=75,40,55,70; pw=width-left-right; ph=height-top-bottom
    dates=sorted(g.date.unique()); xmin=pd.Timestamp(dates[0]); xmax=pd.Timestamp(dates[-1])
    ymin=float(g.employment_index_mar2025_100.min())-0.8; ymax=float(g.employment_index_mar2025_100.max())+0.8
    x=lambda dt: left+(pd.Timestamp(dt)-xmin).days/(xmax-xmin).days*pw
    y=lambda v: top+(ymax-float(v))/(ymax-ymin)*ph
    colours={"Q1 lowest":"#4e79a7","Q2":"#f28e2b","Q3":"#59a14f","Q4 highest":"#e15759"}
    parts=[f'<text x="{width/2}" y="28" text-anchor="middle" class="title">Monthly PAYE employment by LCEI quartile</text>']
    for val in [98,100,102,104]:
        if ymin<=val<=ymax:
            yy=y(val); parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{left+pw}" y2="{yy:.1f}" class="grid"/>')
            parts.append(f'<text x="{left-10}" y="{yy+4:.1f}" text-anchor="end" class="small">{val}</text>')
    policy=x(pd.Timestamp('2025-04-01')); parts.append(f'<line x1="{policy:.1f}" y1="{top}" x2="{policy:.1f}" y2="{top+ph}" stroke="#374151" stroke-dasharray="5,4"/>')
    for q in colours:
        dd=g[g.quartile.astype(str)==q].sort_values('date')
        pts=' '.join(f'{x(r.date):.1f},{y(r.employment_index_mar2025_100):.1f}' for r in dd.itertuples())
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{colours[q]}" stroke-width="2.3"/>')
    years=[pd.Timestamp('2023-01-01'),pd.Timestamp('2024-01-01'),pd.Timestamp('2025-01-01'),pd.Timestamp('2026-01-01'),pd.Timestamp('2026-07-01')]
    for dt in years:
        xx=x(dt); parts.append(f'<text x="{xx:.1f}" y="{height-35}" text-anchor="middle" class="small">{dt:%b %Y}</text>')
    parts.append(f'<text x="{left+pw/2}" y="{height-8}" text-anchor="middle" class="label">Month</text>')
    parts.append(f'<text x="18" y="{top+ph/2}" transform="rotate(-90 18 {top+ph/2})" text-anchor="middle" class="label">Mean PAYE employment index (Mar 2025 = 100)</text>')
    lx=left+15; ly=top+18
    for i,(q,c) in enumerate(colours.items()):
        xx=lx+(i%2)*170; yy=ly+(i//2)*20
        parts.append(f'<line x1="{xx}" y1="{yy}" x2="{xx+22}" y2="{yy}" stroke="{c}" stroke-width="3"/><text x="{xx+28}" y="{yy+4}" class="small">{q}</text>')
    _write_svg(Path(out),width,height,'\n'.join(parts),'Monthly PAYE employment by LCEI quartile')


def event_plot(event: pd.DataFrame, out: Path):
    d=event.sort_values("event_month").copy(); width,height=1000,520; left,right,top,bottom=75,40,55,70; pw=width-left-right; ph=height-top-bottom
    xmin,xmax=float(d.event_month.min()),float(d.event_month.max())
    low=(d.coefficient-1.96*d.clustered_se).min(); high=(d.coefficient+1.96*d.clustered_se).max(); margin=(high-low)*0.08
    ymin,ymax=float(low-margin),float(high+margin)
    x=lambda v:left+(float(v)-xmin)/(xmax-xmin)*pw; y=lambda v:top+(ymax-float(v))/(ymax-ymin)*ph
    parts=[f'<text x="{width/2}" y="28" text-anchor="middle" class="title">Monthly exposure-intensity event study with 95% confidence intervals</text>']
    y0=y(0); parts.append(f'<line x1="{left}" y1="{y0:.1f}" x2="{left+pw}" y2="{y0:.1f}" class="axis"/>')
    policy=x(-0.5); parts.append(f'<line x1="{policy:.1f}" y1="{top}" x2="{policy:.1f}" y2="{top+ph}" stroke="#374151" stroke-dasharray="5,4"/>')
    pts=[]
    for r in d.itertuples():
        xx=x(r.event_month); yy=y(r.coefficient); lo=y(r.coefficient-1.96*r.clustered_se); hi=y(r.coefficient+1.96*r.clustered_se)
        parts.append(f'<line x1="{xx:.1f}" y1="{hi:.1f}" x2="{xx:.1f}" y2="{lo:.1f}" stroke="#4e79a7" stroke-width="1"/>')
        parts.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="2.6" fill="#4e79a7"/>'); pts.append(f'{xx:.1f},{yy:.1f}')
    parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#4e79a7" stroke-width="1.5"/>')
    for val in [-24,-12,0,12,15]:
        if xmin<=val<=xmax:
            xx=x(val); parts.append(f'<text x="{xx:.1f}" y="{height-35}" text-anchor="middle" class="small">{val}</text>')
    parts.append(f'<text x="{left+pw/2}" y="{height-8}" text-anchor="middle" class="label">Month relative to Apr 2025 (Mar 2025 = reference)</text>')
    parts.append(f'<text x="18" y="{top+ph/2}" transform="rotate(-90 18 {top+ph/2})" text-anchor="middle" class="label">LCEI × event-month coefficient (log points)</text>')
    _write_svg(Path(out),width,height,'\n'.join(parts),'Monthly exposure-intensity event study')
