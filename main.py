#!/usr/bin/env python

import sys
from pathlib import Path
import time
import os
import argparse
import boto3
import logging
import uuid
from textwrap import dedent
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from src.utils.bedrock_agent import Agent, SupervisorAgent
# Get the current file's directory
sys.path.append(str(os.path.dirname(os.path.abspath('__file__'))))
from knowledge_base import KnowledgeBasesForAmazonBedrock


kb_helper = KnowledgeBasesForAmazonBedrock()

s3_client = boto3.client('s3')
sts_client = boto3.client('sts')

logging.basicConfig(format='[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def upload_directory(path, bucket_name):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_to_upload = os.path.join(root, file)
            dest_key = f"{path}/{file}"
            print(f"파일 업로드 중: {file_to_upload} -> {bucket_name}")
            s3_client.upload_file(file_to_upload, bucket_name, dest_key)


def main(args):
    if args.clean_up == "true":
        Agent.set_force_recreate_default(True)
        Agent.delete_by_name("skt_chatops_assistant", verbose=True)
        kb_helper.delete_kb("service-kb", delete_s3_bucket=False)
        return
    if args.recreate_agents == "false":
        Agent.set_force_recreate_default(False)
    else:
        Agent.set_force_recreate_default(True)
        Agent.delete_by_name("skt_chatops_assistant", verbose=True)

    bucket_name = None
    print("서비스 지식베이스 생성 중...")
    kb_name = "service-kb"
    kb_id, ds_id = kb_helper.create_or_retrieve_knowledge_base(
        kb_name,
        kb_description="서비스 담당자 정보 및 과거 오류 사례에 대한 지식베이스",
        data_bucket_name=bucket_name,
        chunking_strategy="CUSTOM"
    )
    bucket_name = kb_helper.data_bucket_name
    print(f"KB 이름: {kb_name}, kb_id: {kb_id}, ds_id: {ds_id}, s3 버킷 이름: {bucket_name}\n")

    if args.recreate_agents == "true":
        print("디렉토리 업로드 중...")
        upload_directory("knowledge_dataset", f"{bucket_name}")

        # KB가 사용 가능해질 때까지 대기
        time.sleep(30)
        # 지식베이스 동기화
        kb_helper.synchronize_data(kb_id, ds_id)
        print('KB 동기화 완료\n')

    # Agent 1: 로그 분석 에이전트
    log_analysis_agent = Agent.create(
        name="log_analysis_agent",
        role="Datadog 로그 분석 전문가",
        goal="Datadog에서 수집된 로그를 분석하여 오류 원인과 해결책을 제시합니다.",
        instructions=dedent("""
        당신은 Datadog에서 수집된 로그를 분석하는 전문가입니다.
        주어진 Trace ID와 시간 범위에 따라 로그를 검색하고, 다음과 같은 분석을 수행하세요:
        1. 오류 메시지나 예외(Exception)를 식별하고 요약
        2. 문제의 근본 원인 파악
        3. 문제 해결책 제안
        4. 영향받는 클라이언트가 있다면 해당 정보 제공
        
        JSON 형식으로 구조화된 응답을 제공하세요.
        """),
        tool_code="log_analysis_function.py",
        tool_defs=[
            {
                "name": "search_logs_by_trace",
                "description": "주어진 Trace ID를 기반으로 특정 시간 범위 내의 Datadog 로그를 검색합니다.",
                "parameters": {
                    "trace_id": {
                        "description": "검색할 Trace ID",
                        "type": "string",
                        "required": True
                    },
                    "from_ts": {
                        "description": "검색 시작 타임스탬프 (밀리초)",
                        "type": "string", 
                        "required": True
                    },
                    "to_ts": {
                        "description": "검색 종료 타임스탬프 (밀리초)",
                        "type": "string",
                        "required": True
                    },
                    "service": {
                        "description": "검색할 서비스 이름",
                        "type": "string",
                        "required": True
                    },
                    "env": {
                        "description": "검색할 환경 (예: prd-bo, stg)",
                        "type": "string",
                        "required": True
                    }
                }
            }
        ],
        llm="us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    )

    # Agent 2: 리소스 분석 에이전트
    resource_analysis_agent = Agent.create(
        name="resource_analysis_agent",
        role="리소스 상태 분석 전문가",
        goal="서비스의 CPU 및 메모리 사용률을 분석하여 리소스 관련 문제를 식별합니다.",
        instructions=dedent("""
        당신은 Datadog에서 수집된 리소스 메트릭을 분석하는 전문가입니다.
        주어진 서비스, 환경, 시간 범위에 따라 다음과 같은 분석을 수행하세요:
        1. CPU 사용률 분석
        2. 메모리 사용률 분석
        3. 리소스 부족으로 인한 문제 발생 여부 판단
        4. 리소스 부족이 확인된 경우 권장 조치 제안
        
        JSON 형식으로 구조화된 응답을 제공하세요.
        """),
        tool_code="resource_analysis_function.py",
        tool_defs=[
            {
                "name": "get_resource_metrics",
                "description": "주어진 서비스와 시간 범위에 대한 리소스(CPU, 메모리) 메트릭을 조회합니다.",
                "parameters": {
                    "service": {
                        "description": "조회할 서비스 이름",
                        "type": "string",
                        "required": True
                    },
                    "env": {
                        "description": "조회할 환경 (예: prd-bo, stg)",
                        "type": "string",
                        "required": True
                    },
                    "from_ts": {
                        "description": "조회 시작 타임스탬프 (밀리초)",
                        "type": "string",
                        "required": True
                    },
                    "to_ts": {
                        "description": "조회 종료 타임스탬프 (밀리초)",
                        "type": "string",
                        "required": True
                    }
                }
            }
        ],
        llm="us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    )

    # Agent 3: 담당자 및 과거 사례 검색 에이전트
    kb_search_agent = Agent.create(
        name="kb_search_agent",
        role="서비스 담당자 및 과거 사례 검색 전문가",
        goal="서비스별 담당자 정보와 유사한 과거 사례를 검색하여 제공합니다.",
        instructions=dedent("""
        당신은 서비스별 담당자 정보와 과거 사례를 검색하는 전문가입니다.
        지식베이스를 검색할 때 다음 사항에 특히 주의하세요:
        
        1. 서비스 담당자 검색:
           - 정확한 서비스명으로 검색하여 모듈 담당자와 개발 담당자 정보를 찾으세요.
           - JSON 구조에서 담당자 정보는 'responsible_parties' 필드에 있습니다.
           - 완전한 JSON 객체에서만 정보를 추출하고, 불완전한 데이터는 무시하세요.
           - 담당자 정보가 명확하지 않은 경우 '담당자 정보를 찾을 수 없습니다'라고 응답하세요.
        
        2. 과거 유사 사례 검색:
           - 동일한 오류 로그, API, 메시지가 있는 과거 사례만 제시하세요.
           - 유사성이 낮은 사례는 제외하세요.
           - 과거 사례가 발견된 경우 발생 시간과 해결 방법을 포함하세요.
        
        지식베이스 검색 결과를 JSON 형식으로 구조화하여 응답하세요.
        """),
        kb_id=kb_id,
        kb_descr="서비스별 담당자 정보 및 과거 오류 사례에 관한 지식베이스입니다.",
        llm="us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    )

    # 슈퍼바이저 에이전트 생성
    chatops_assistant = SupervisorAgent.create(
        "skt_chatops_assistant",
        role="SKT 구독팀 ChatOps 어시스턴트",
        goal="Datadog 알림을 분석하여 서비스 장애에 대한 종합적인 정보를 제공합니다.",
        collaboration_type="SUPERVISOR",
        instructions=dedent(f"""
        당신은 SKT 구독팀의 ChatOps 전문가로, Datadog에서 특정 Trace ID를 기반으로 로그와 메트릭을 분석하고 RAG 검색을 통해 종합적인 정보를 제공합니다.
        
        Multi Agent를 실행하는 경우 각 에이전트를 병렬로 실행해주세요.
        
        사용자의 요청을 분석하여 다음 세 가지 분석을 수행하세요:
        1. Datadog 로그 분석: 오류 메시지, 예외(Exception) 내용 기반 상세 분석
        2. 리소스 상태 분석: CPU 및 메모리 사용률 확인 및 평가
        3. 서비스 담당자 및 과거 이력 분석: 담당자 정보 및 유사 사례 확인
        
        응답 형식:
        1️⃣ Datadog Log (message/exception) 분석 결과
        1) 분석 결과 요약: (최대 5개 항목)
        2) 오류 원인: (최대 2줄)
        3) 해결책: (최대 3개 항목)
        
        2️⃣ 리소스 상태 분석 결과
        1) CPU 사용률: (%)
        2) Memory 사용률: (%)
        - 리소스 상태 평가
        
        3️⃣ 담당자 및 과거 이력:
        1) 서비스 담당자: (모듈 담당자) / (개발 담당자)
        2) 과거 유사 사례: (발생 시간 및 해결 방식)
        """),
        collaborator_agents=[
            {
                "agent": "log_analysis_agent",
                "instructions": "Datadog 로그 분석을 수행하여 오류 메시지와 예외를 분석하고 해결책을 제시하는 데 사용합니다.",
            },
            {
                "agent": "resource_analysis_agent",
                "instructions": "서비스의 CPU 및 메모리 사용률을 분석하여 리소스 관련 문제를 식별하는 데 사용합니다.",
            },
            {
                "agent": "kb_search_agent",
                "instructions": "서비스 담당자 정보와 과거 유사 사례를 검색하는 데 사용합니다. 지식베이스 검색 시 정확한 정보만 추출하세요.",
            }
        ],
        collaborator_objects=[
            log_analysis_agent,
            resource_analysis_agent,
            kb_search_agent
        ],
        llm="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        verbose=False
    )

    if args.recreate_agents == "false":
        print("\n\n슈퍼바이저 에이전트 호출 중...\n\n")

        session_id = str(uuid.uuid4())

        request = """
        env: prd-bo 
        service: fsp-pay-gateway
        from_ts: 1702441545000 
        to_ts: 1742441905000 
        trace_id: 67db8cf2000000003f2339dd4b4e1398
        """

        print(f"\n\n요청: {request}\n\n")
        result = chatops_assistant.invoke(request, session_id=session_id,
                                        enable_trace=True, trace_level=args.trace_level)
        print(result)


if __name__ == '__main__':
    print("메인 프로그램 시작")
    parser = argparse.ArgumentParser()
    parser.add_argument("--recreate_agents", required=False, default="true", help="False: 기존 에이전트 재사용, True: 에이전트 새로 생성")
    parser.add_argument("--clean_up", required=False, default="false", help="True: 에이전트 리소스 정리")
    parser.add_argument("--trace_level", required=False, default="core", help="트레이스 레벨: 'core', 'outline', 'all'")

    args = parser.parse_args()
    main(args)
