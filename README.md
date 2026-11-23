# 삼성전자 OpenDART 재무 분석 에이전트

OpenDART API를 활용해 삼성전자의 재무 데이터를 자동 수집하고, 주요 재무 지표를 분석하며, 보고서와 웹 대시보드를 생성하는 프로젝트입니다.


## 📊 대시보드 바로가기

[삼성전자 재무 분석 대시보드 열기](https://hsc-class02.github.io/sb_samsung/)

## 주요 기능
- 삼성전자 사업보고서·반기보고서·분기보고서 재무 데이터 수집
- 연결재무제표 우선 분석
- 주요 재무비율 계산 및 데이터 검증
- 재무 분석 보고서(Markdown) 자동 생성
- GitHub Pages 대시보드 제공
- 매월 1일 자동 업데이트 및 수동 실행 지원

## 실행 및 설정
1. 저장소 **Settings → Secrets and variables → Actions**에서 `DART_API_KEY` Secret을 등록합니다.
2. **Actions → DART Financial Agent → Run workflow**를 선택해 수동 실행합니다.
3. **Settings → Pages**에서 배포 소스를 **GitHub Actions**로 설정합니다.

## 주요 결과물
- 재무 분석 보고서: `reports/financial_analysis.md`
- 대시보드: GitHub Pages
- 재무 데이터: `data/financials.csv`, `data/metrics.csv`
- 대시보드 데이터: `dashboard/data.json`

## 분석 범위 및 기준
- 대상 기업: 삼성전자 (고유번호 `00126380`)
- 수집 시작 연도: 2015년
- 보고서 유형: 사업보고서(`11011`), 반기보고서(`11012`), 1분기보고서(`11013`), 3분기보고서(`11014))
- 데이터 제공: 금융감독원 OpenDART
- 본 프로젝트는 학습 및 참고 목적이며 투자 권유가 아닙니다. 보고서별 계정명과 데이터 제공 범위가 다를 수 있습니다.
