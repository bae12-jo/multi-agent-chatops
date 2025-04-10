# Multi-agent collaboration을 활용한 ChatOps 시스템

이 프로젝트는 Datadog과 Amazon Bedrock을 활용하여 서비스 장애 분석 및 대응을 자동화하는 ChatOps 시스템입니다.

## 구성 요소

Multi-agent 협업 시스템
   - Agent 1: Datadog 로그 분석
   - Agent 2: 리소스 상태 분석
   - Agent 3: 담당자 및 과거 사례 검색

주요 구성 요소는 다음과 같습니다:

1. **3개의 에이전트**:
   - `log_analysis_agent`: Datadog 로그를 분석하여 오류 원인과 해결책 제시
   - `resource_analysis_agent`: CPU 및 메모리 사용률 분석
   - `kb_search_agent`: 서비스 담당자 및 과거 사례 검색

2. **지식베이스 데이터**:
   - `service_owners.json`: 서비스별 담당자 정보 (JSON 형식으로 구조화)
   - `past_issues.json`: 과거 오류 사례 정보

3. **슈퍼바이저 에이전트**: 병렬로 세 에이전트를 실행하고 결과를 종합하여 제공

특히 KB 검색 에이전트의 instruction에 JSON 형식 데이터 처리를 위한 명확한 지침을 추가하여, 담당자 정보를 정확히 추출할 수 있도록 했습니다.

## 사용 방법

1. 에이전트 배포:
```bash
cd skt_chatops
python main.py --recreate_agents "true"
```

2. 실행:
```bash
python main.py --recreate_agents "false"
```

3. 리소스 정리:
```bash
python main.py --clean_up "true"
```
