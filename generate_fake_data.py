import json
import random
import datetime

# 한국 이름 목록 (성과 이름 분리)
last_names = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임", "한", "오", "서", "신", "권", "황", "안", "송", "류", "전", "홍", "고", "문", "양", "손", "배", "조", "백", "허", "유", "남", "심", "노", "정", "하", "곽", "성", "차", "주", "우", "구", "신", "임", "나", "전", "민", "유", "진", "지", "엄", "채", "원", "천", "방", "공", "강", "현", "함", "변", "염", "양"]
first_names = ["민준", "서준", "예준", "도윤", "시우", "주원", "하준", "지호", "지후", "준서", "준우", "현우", "도현", "지훈", "건우", "우진", "민재", "현준", "선우", "서진", "연우", "정우", "민성", "중혁", "성훈", "성현", "성민", "지훈", "지민", "현민", "지원", "소민", "수민", "민지", "정민", "유진", "진우", "가은", "민주", "나은", "서연", "지은", "서현", "하은", "현정", "예지", "지현", "윤아", "가현", "하늘", "소윤", "아름", "경희", "민수", "경수", "성현", "재민", "성준", "영호", "동현"]

# 서비스 구성 요소
service_prefixes = ["ssp", "msp", "csp", "dsp", "esp", "fsp", "gsp", "hsp", "isp", "jsp", "ksp", "lsp", "nsp", "osp", "psp", "qsp", "rsp", "tsp", "usp", "vsp", "wsp", "xsp", "ysp", "zsp"]
service_types = ["api", "bff", "bat", "core", "auth", "admin", "data", "sync", "proc", "queue", "cache", "search", "rec", "msg", "noti", "pay", "user", "order"]
service_suffixes = ["core", "bo", "fo", "dis", "mgr", "srv", "engine", "handler", "worker", "proc", "svc", "util", "helper", "gateway", "proxy", "store", "client", "service", "cmp", "com", "dcp"]

# 오류 유형 및 해결 방안
error_templates = [
    {
        "error_message": "java.io.IOException: Connection reset by peer", 
        "resolutions": [
            "네트워크 타임아웃 설정 조정 및 재시도 로직 추가",
            "커넥션 풀 설정 최적화 및 안정성 개선",
            "네트워크 모니터링 강화 및 장애 복구 로직 구현"
        ]
    },
    {
        "error_message": "java.net.SocketTimeoutException: Read timed out", 
        "resolutions": [
            "타임아웃 설정 증가 및 백오프 전략 적용",
            "클라이언트 소켓 설정 최적화 및 재시도 로직 추가",
            "서비스 간 통신 타임아웃 파라미터 재설정"
        ]
    },
    {
        "error_message": "java.sql.SQLException: ORA-01000: maximum open cursors exceeded", 
        "resolutions": [
            "커넥션 풀 설정 조정 및 쿼리 최적화",
            "DB 세션 관리 개선 및 리소스 해제 로직 점검",
            "쿼리 캐싱 전략 적용 및 커서 사용 최적화"
        ]
    },
    {
        "error_message": "java.lang.OutOfMemoryError: Java heap space", 
        "resolutions": [
            "JVM 힙 메모리 설정 증가 및 메모리 누수 패턴 분석",
            "대용량 객체 처리 로직 개선 및 메모리 사용량 최적화",
            "가비지 컬렉션 파라미터 튜닝 및 모니터링 강화"
        ]
    },
    {
        "error_message": "org.springframework.dao.DataIntegrityViolationException: Duplicate entry", 
        "resolutions": [
            "중복 키 처리 로직 추가 및 트랜잭션 관리 강화",
            "동시성 제어 메커니즘 구현 및 락 전략 개선",
            "고유 인덱스 설계 검토 및 비즈니스 로직 수정"
        ]
    },
    {
        "error_message": "javax.persistence.PersistenceException: Transaction timeout", 
        "resolutions": [
            "트랜잭션 타임아웃 증가 및 대용량 작업 분할 처리",
            "DB 인덱스 최적화 및 트랜잭션 크기 축소",
            "비동기 처리 방식으로 변경 및 작업 단위 조정"
        ]
    },
    {
        "error_message": "org.springframework.web.client.ResourceAccessException: I/O error", 
        "resolutions": [
            "외부 API 통신 안정성 강화 및 장애 대응 로직 구현",
            "서킷브레이커 패턴 적용 및 폴백 메커니즘 구현",
            "네트워크 재시도 정책 적용 및 타임아웃 설정 조정"
        ]
    },
    {
        "error_message": "redis.clients.jedis.exceptions.JedisConnectionException: Could not get a resource from the pool", 
        "resolutions": [
            "Redis 커넥션 풀 설정 최적화 및 상태 모니터링 추가",
            "Redis 클러스터 확장 및 고가용성 구성 검토",
            "캐시 사용 전략 개선 및 대체 메커니즘 구현"
        ]
    },
    {
        "error_message": "java.util.concurrent.TimeoutException: Timeout waiting for task", 
        "resolutions": [
            "쓰레드 풀 설정 조정 및 작업 타임아웃 증가",
            "비동기 작업 처리 로직 최적화 및 모니터링 강화",
            "장기 실행 작업 분할 처리 및 진행 상태 추적 기능 추가"
        ]
    },
    {
        "error_message": "org.hibernate.StaleObjectStateException: Row was updated or deleted by another transaction", 
        "resolutions": [
            "낙관적 락 전략 적용 및 충돌 해결 로직 구현",
            "버전 관리 메커니즘 도입 및 동시성 제어 개선",
            "트랜잭션 격리 수준 조정 및 재시도 로직 추가"
        ]
    },
    {
        "error_message": "com.fasterxml.jackson.core.JsonParseException: Unexpected character", 
        "resolutions": [
            "JSON 파싱 예외 처리 강화 및 유효성 검증 로직 추가",
            "직렬화/역직렬화 예외 처리 개선 및 데이터 정제 과정 추가",
            "API 요청/응답 포맷 검증 로직 강화"
        ]
    },
    {
        "error_message": "org.elasticsearch.transport.RemoteTransportException: Failed to deserialize response", 
        "resolutions": [
            "Elasticsearch 클라이언트 버전 호환성 검토 및 업데이트",
            "데이터 모델 일관성 유지 및 마이그레이션 스크립트 적용",
            "검색 쿼리 최적화 및 오류 처리 로직 개선"
        ]
    },
    {
        "error_message": "java.lang.IllegalStateException: Queue full", 
        "resolutions": [
            "메시지 큐 용량 증설 및 백프레셔 메커니즘 구현",
            "생산자 조절 로직 추가 및 소비자 처리 속도 최적화",
            "큐 모니터링 강화 및 부하 분산 전략 적용"
        ]
    },
    {
        "error_message": "org.apache.kafka.common.errors.RecordTooLargeException: The message is too large", 
        "resolutions": [
            "메시지 크기 제한 설정 조정 및 대용량 메시지 분할 처리",
            "압축 알고리즘 적용 및 페이로드 최적화",
            "메시지 처리 파이프라인 재설계 및 저장 전략 변경"
        ]
    },
    {
        "error_message": "java.lang.NullPointerException", 
        "resolutions": [
            "널 체크 로직 추가 및 방어적 프로그래밍 적용",
            "Optional 활용 및 코드 안정성 개선",
            "단위 테스트 강화 및 엣지 케이스 처리"
        ]
    },
]

# 서비스 설명 생성 함수
def generate_service_description():
    service_types_desc = {
        "api": ["API", "RESTful API", "GraphQL API", "외부 연동 API"],
        "bff": ["BFF", "Backend-For-Frontend", "프론트엔드 중계"],
        "bat": ["배치", "일괄 처리", "정기 작업", "스케줄러", "배치 처리"],
        "core": ["코어", "핵심 기능", "플랫폼 핵심"],
        "auth": ["인증", "권한", "계정 관리"],
        "admin": ["관리자", "어드민", "운영자"],
        "data": ["데이터", "데이터 처리", "데이터 관리"],
        "sync": ["동기화", "실시간 연동", "상태 동기화"],
        "proc": ["처리기", "프로세서", "연산 엔진"],
        "queue": ["큐", "메시지 큐", "작업 대기열"],
        "cache": ["캐시", "임시 저장소", "메모리 스토리지"],
        "search": ["검색", "조회", "탐색 엔진"],
        "rec": ["추천", "개인화", "큐레이션"],
        "msg": ["메시징", "알림", "커뮤니케이션"],
        "noti": ["알림", "푸시", "메시지"],
        "pay": ["결제", "금융", "정산"],
        "user": ["사용자", "회원", "고객"],
        "order": ["주문", "예약", "거래"],
        "cmp": ["구성 요소", "컴포넌트", "모듈"],
        "com": ["통신", "커뮤니케이션", "공통"],
        "dcp": ["데이터 처리", "쿠폰", "분산"]
    }

    business_domains = [
        "구독 서비스", "회원 서비스", "콘텐츠 서비스", "상품 서비스", "결제 서비스",
        "배송 서비스", "재고 관리", "포인트 서비스", "쿠폰 서비스", "알림 서비스",
        "검색 서비스", "추천 서비스", "리뷰 서비스", "광고 서비스", "정산 서비스",
        "통계 서비스", "고객 서비스", "마케팅 서비스", "이벤트 서비스", "인증 서비스"
    ]
    
    domain = random.choice(business_domains)
    service_type = random.choice(list(service_types_desc.keys()))
    type_desc = random.choice(service_types_desc.get(service_type, ["서비스"]))
    
    return f"{domain} {type_desc}"

# 담당자 배열 생성 함수
def generate_responsible_parties(min_people=0, max_people=3):
    num_people = random.randint(min_people, max_people)
    if num_people == 0:
        return []
    
    people = []
    used_names = set()
    
    for _ in range(num_people):
        name = random.choice(last_names) + random.choice(first_names)
        # 중복 방지
        while name in used_names:
            name = random.choice(last_names) + random.choice(first_names)
        used_names.add(name)
        people.append(name)
    
    return people

# 날짜 생성 함수 (최근 2년 이내)
def generate_random_date():
    end_date = datetime.datetime(2025, 6, 30)
    start_date = datetime.datetime(2023, 7, 1)
    
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_days)
    
    # 시간, 분, 초 추가
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    
    random_date = random_date.replace(hour=random_hour, minute=random_minute, second=random_second)
    
    return random_date.strftime("%Y-%m-%d %H:%M:%S")

# 무작위 트레이스 ID 생성
def generate_trace_id():
    hex_chars = "0123456789abcdef"
    trace_id = ""
    
    # 32자리 16진수 ID 생성 (8+8+8+8자리 포맷)
    for i in range(32):
        trace_id += random.choice(hex_chars)
    
    return trace_id[:8] + "00000000" + trace_id[16:24] + trace_id[24:]

# 서비스 이름 생성 함수
def generate_service_names(count=100):
    service_names = set()
    
    while len(service_names) < count:
        prefix = random.choice(service_prefixes)
        type_comp = random.choice(service_types)
        suffix = random.choice(service_suffixes)
        service_name = f"{prefix}-{type_comp}-{suffix}"
        service_names.add(service_name)
    
    return list(service_names)

# 주 함수: 서비스 데이터 및 과거 이슈 생성
def generate_data(service_count=100, issue_count=200):
    # 서비스 이름 목록 생성
    service_names = generate_service_names(service_count)
    
    # 서비스 소유자 정보 생성
    services = {}
    for service_name in service_names:
        # 담당자 생성 (배열로)
        module_owners = generate_responsible_parties(1, 2)  # 최소 1명, 최대 2명
        dev_owners = generate_responsible_parties(0, 3)     # 0~3명
        
        services[service_name] = {
            "description": generate_service_description(),
            "responsible_parties": {
                "모듈 담당자": module_owners,
                "개발 담당자": dev_owners
            },
            "비고": ""
        }
    
    # 과거 이슈 생성
    past_issues = []
    for _ in range(issue_count):
        service_name = random.choice(service_names)
        error_template = random.choice(error_templates)
        
        issue = {
            "service": service_name,
            "error_message": error_template["error_message"],
            "timestamp": generate_random_date(),
            "resolution": random.choice(error_template["resolutions"]),
            "trace_id": generate_trace_id()
        }
        past_issues.append(issue)
    
    # 생성된 이슈를 timestamp 기준으로 내림차순 정렬 (최근 이슈가 위로)
    past_issues.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return services, past_issues

# 데이터 생성
services, past_issues = generate_data(100, 200)

# 서비스 소유자 정보 출력 및 저장
print("===== 서비스 소유자 정보 =====")
print(json.dumps(services, ensure_ascii=False, indent=2)[:500] + "...\n")

with open('service_owners.json', 'w', encoding='utf-8') as f:
    json.dump(services, f, ensure_ascii=False, indent=2)

# 과거 이슈 정보 출력 및 저장
print("===== 과거 이슈 정보 =====")
print(json.dumps(past_issues, ensure_ascii=False, indent=2)[:500] + "...\n")

with open('past_issues.json', 'w', encoding='utf-8') as f:
    json.dump(past_issues, f, ensure_ascii=False, indent=2)

print(f"생성 완료: 서비스 {len(services)}개, 이슈 {len(past_issues)}개")
