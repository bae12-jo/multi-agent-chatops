from datetime import datetime
import random

def get_named_parameter(event, name):
    if 'parameters' in event:
        item = next((item for item in event['parameters'] if item['name'] == name), None)
        return item['value'] if item else None
    else:
        return None
    
def populate_function_response(event, response_body):
    return {'response': {'actionGroup': event['actionGroup'], 'function': event['function'],
                'functionResponse': {'responseBody': {'TEXT': {'body': str(response_body)}}}}}

def get_resource_metrics(service, env, from_ts, to_ts):
    # 실제로는 Datadog API를 호출하여 메트릭을 검색하겠지만,
    # 데모 목적으로 샘플 데이터 반환
    
    # 타임스탬프를 읽기 쉬운 형식으로 변환
    from_date = datetime.fromtimestamp(int(from_ts)/1000).strftime('%Y-%m-%d %H:%M:%S')
    to_date = datetime.fromtimestamp(int(to_ts)/1000).strftime('%Y-%m-%d %H:%M:%S')
    
    # CPU 사용률 - 임의로 40~50% 사이 값 생성
    cpu_usage = round(random.uniform(40, 50), 1)
    
    # 메모리 사용률 - 임의로 60~80% 사이 값 생성
    memory_usage = round(random.uniform(60, 80), 1)
    
    return {
        "service": service,
        "environment": env,
        "time_period": {
            "from": from_date,
            "to": to_date
        },
        "cpu": {
            "avg_usage_percent": cpu_usage,
            "max_usage_percent": round(cpu_usage + random.uniform(5, 10), 1),
            "min_usage_percent": round(cpu_usage - random.uniform(5, 10), 1)
        },
        "memory": {
            "avg_usage_percent": memory_usage,
            "max_usage_percent": round(memory_usage + random.uniform(5, 10), 1),
            "min_usage_percent": round(memory_usage - random.uniform(5, 10), 1)
        },
        "analysis": {
            "is_cpu_critical": False,
            "is_memory_critical": False,
            "is_resource_related_issue": False
        }
    }

def lambda_handler(event, context):
    print(event)
    function = event['function']
    
    if function == 'get_resource_metrics':
        service = get_named_parameter(event, 'service')
        env = get_named_parameter(event, 'env')
        from_ts = get_named_parameter(event, 'from_ts')
        to_ts = get_named_parameter(event, 'to_ts')
        
        result = get_resource_metrics(service, env, from_ts, to_ts)
    else:
        result = f"오류: 함수 '{function}'를 인식할 수 없습니다"

    response = populate_function_response(event, result)
    print(response)
    return response
