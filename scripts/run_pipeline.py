#!/usr/bin/env python3
"""Fetch Samsung Electronics OpenDART statements, validate, summarize, and export."""
import os, sys, time
from pathlib import Path
import requests
import pandas as pd

API_KEY = os.getenv('DART_API_KEY')
CORP_CODE = '00126380'
BASE = 'https://opendart.fss.or.kr/api'
OUT = Path(__file__).resolve().parents[1]
DATA = OUT / 'data'
REPORTS = OUT / 'reports'
DASH = OUT / 'dashboard'
DATA.mkdir(exist_ok=True); REPORTS.mkdir(exist_ok=True); DASH.mkdir(exist_ok=True)


def dart(endpoint, params):
    if not API_KEY: raise RuntimeError('DART_API_KEY environment secret is missing')
    params = dict(params, crtfc_key=API_KEY)
    resp = requests.get(f'{BASE}/{endpoint}.json', params=params, timeout=30)
    resp.raise_for_status(); body = resp.json()
    if body.get('status') not in ('000', '013'):
        raise RuntimeError('OpenDART {}: {} {}'.format(endpoint, body.get('status'), body.get('message')))
    return body


def collect():
    rows=[]
    # Annual filings are collected first; quarterly/half-year records are also retained.
    for year in range(2015, pd.Timestamp.today().year + 1):
        for code, label in [('11011','Annual'),('11012','Semiannual'),('11013','Q1'),('11014','Q3')]:
            try:
                result=dart('fnlttSinglAcntAll', {'corp_code':CORP_CODE,'bsns_year':str(year),'reprt_code':code,'fs_div':'CFS'})
                items=result.get('list', [])
                if not items: continue
                # Account names vary slightly across filing versions. Match by Korean account labels.
                vals={item.get('account_nm',''):item.get('thstrm_amount') for item in items}
                def find(*keys):
                    for key in keys:
                        for name,value in vals.items():
                            if key in name and value not in (None,'','-'):
                                try: return float(str(value).replace(',',''))
                                except ValueError: pass
                    return None
                revenue=find('매출액','수익(매출액)')
                op=find('영업이익')
                ni=find('당기순이익','당기순손익')
                assets=find('자산총계'); liabilities=find('부채총계'); equity=find('자본총계')
                ca=find('유동자산'); cl=find('유동부채'); cash=find('현금및현금성자산')
                ocf=find('영업활동현금흐름')
                if revenue is None and op is None: continue
                row={'year':year,'report_code':code,'report':label,'revenue':revenue,'operating_profit':op,'net_income':ni,'assets':assets,'liabilities':liabilities,'equity':equity,'current_assets':ca,'current_liabilities':cl,'cash':cash,'ocf':ocf}
                row['operating_margin']=op/revenue*100 if revenue and op is not None else None
                row['net_margin']=ni/revenue*100 if revenue and ni is not None else None
                row['debt_ratio']=liabilities/equity*100 if liabilities is not None and equity else None
                row['equity_ratio']=equity/assets*100 if equity is not None and assets else None
                row['current_ratio']=ca/cl*100 if ca is not None and cl else None
                row['roa']=ni/assets*100 if ni is not None and assets else None
                row['roe']=ni/equity*100 if ni is not None and equity else None
                row['ocf_ratio']=ocf/revenue*100 if ocf is not None and revenue else None
                # Basic balance validation, where all components are present.
                row['validated']=abs(assets-liabilities-equity) <= max(abs(assets)*0.015, 1e8) if all(x is not None for x in (assets,liabilities,equity)) else None
                rows.append(row)
                time.sleep(0.12)
            except Exception as e:
                print(f'WARN {year}/{code}: {e}', file=sys.stderr)
    df=pd.DataFrame(rows)
    if df.empty: raise RuntimeError('No financial statement records collected. Check API key, connectivity, and filing availability.')
    df=df.drop_duplicates(['year','report_code']).sort_values(['year','report_code'])
    df.to_csv(DATA/'financials.csv', index=False, encoding='utf-8-sig')
    metrics=df[['year','report_code','report','revenue','operating_profit','net_income','assets','liabilities','equity','operating_margin','net_margin','debt_ratio','current_ratio','roa','roe','ocf_ratio','validated']]
    metrics.to_csv(DATA/'metrics.csv', index=False, encoding='utf-8-sig')
    DASH.mkdir(exist_ok=True)
    (DASH/'data.json').write_text(df.where(pd.notna(df),None).to_json(orient='records',force_ascii=False),encoding='utf-8')
    make_report(df)
    print(f'Collected {len(df)} records')


def fmt(v, unit='T KRW'):
    if pd.isna(v): return 'N/A'
    return f'{v/1e12:,.1f} {unit}'


def make_report(df):
    annual=df[df.report_code=='11011'].sort_values('year')
    lines=['# 삼성전자 재무 분석 보고서','',f'생성 일시: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}','','데이터 출처: 금융감독원 OpenDART (연결재무제표 기준)','']
    if annual.empty: annual=df.sort_values('year')
    latest=annual.iloc[-1]
    lines += ['## 최신 연간 실적 요약','',f'- 기준 연도: {int(latest.year)}',f'- 매출: {fmt(latest.revenue)}',f'- 영업이익: {fmt(latest.operating_profit)}',f'- 당기순이익: {fmt(latest.net_income)}',f'- 영업이익률: {latest.operating_margin:.1f}%' if pd.notna(latest.operating_margin) else '- 영업이익률: 데이터 없음',f'- 부채비율: {latest.debt_ratio:.1f}%' if pd.notna(latest.debt_ratio) else '- 부채비율: 데이터 없음',f'- 유동비율: {latest.current_ratio:.1f}%' if pd.notna(latest.current_ratio) else '- 유동비율: 데이터 없음','', '## 연도별 실적 추이','', '| 연도 | 매출 (조원) | 영업이익 (조원) | 당기순이익 (조원) | 영업이익률 | 부채비율 | 유동비율 |','|---|---:|---:|---:|---:|---:|---:|']
    for _,r in annual.tail(10).iterrows():
        def val(x): return f'{x/1e12:.1f}' if pd.notna(x) else '—'
        def pct(x): return f'{x:.1f}%' if pd.notna(x) else '—'
        lines.append(f'| {int(r.year)} | {val(r.revenue)} | {val(r.operating_profit)} | {val(r.net_income)} | {pct(r.operating_margin)} | {pct(r.debt_ratio)} | {pct(r.current_ratio)} |')
    lines += ['', '## 데이터 검증',f'- 수집 데이터: {len(df)}',f'- 재무상태표 등식 검증 통과: {int(df.validated.sum()) if df.validated.notna().any() else 0}',f'- 검증 실패: {int((df.validated==False).sum())}', '', '## 해석 참고', '매출, 수익성, 유동성 및 재무 안정성 지표를 함께 확인해야 합니다. 보고서별 계정 분류나 데이터 제공 범위가 다를 수 있으며, 누락 값은 0으로 간주하지 않습니다. 연도별 변동은 반도체 수요, 제품 구성, 환율, 설비투자 및 현금흐름 등과 함께 검토하세요. 본 보고서는 학습 및 참고 목적이며 투자 권유가 아닙니다.','']
    (REPORTS/'financial_analysis.md').write_text('\n'.join(lines),encoding='utf-8')

if __name__=='__main__': collect()
