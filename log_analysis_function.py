from datetime import datetime

def get_named_parameter(event, name):
    if 'parameters' in event:
        item = next((item for item in event['parameters'] if item['name'] == name), None)
        return item['value'] if item else None
    else:
        return None
    
def populate_function_response(event, response_body):
    return {'response': {'actionGroup': event['actionGroup'], 'function': event['function'],
                'functionResponse': {'responseBody': {'TEXT': {'body': str(response_body)}}}}}

def search_logs_by_trace(trace_id, from_ts, to_ts, service, env):
    # 실제로는 Datadog API를 호출하여 로그를 검색하겠지만,
    # 데모 목적으로 샘플 데이터 반환
    
    # 타임스탬프를 읽기 쉬운 형식으로 변환
    from_date = datetime.fromtimestamp(int(from_ts)/1000).strftime('%Y-%m-%d %H:%M:%S')
    to_date = datetime.fromtimestamp(int(to_ts)/1000).strftime('%Y-%m-%d %H:%M:%S')
    
    # 샘플 로그 데이터
    return {
        "logs": [
            {
                "timestamp": "2025-03-11 13:47:22.804",
                "service": service,
                "environment": env,
                "trace_id": trace_id,
                "message": "java.io.IOException: Connection reset by peer",
                "stack_trace": "at java.net.SocketInputStream.read(SocketInputStream.java:210)\nat java.net.SocketInputStream.read(SocketInputStream.java:141)\nat java.io.BufferedInputStream.fill(BufferedInputStream.java:246)\nat java.io.BufferedInputStream.read1(BufferedInputStream.java:286)\nat java.io.BufferedInputStream.read(BufferedInputStream.java:345)\nat org.apache.http.impl.io.SessionInputBufferImpl.streamRead(SessionInputBufferImpl.java:139)",
                "path": "/fsp-pay-gateway/DSP/API/Communication",
                "status_code": 500,
                "request_id": "req-12345"
            },
            {
                "timestamp": "2025-03-11 13:47:21.621",
                "service": service,
                "environment": env,
                "trace_id": trace_id,
                "message": "Request processing failed",
                "error_details": "Communication with downstream service failed"
            }
        ],
        "search_metadata": {
            "trace_id": trace_id,
            "service": service,
            "environment": env,
            "from": from_date,
            "to": to_date,
            "log_count": 2
        }
    }

def lambda_handler(event, context):
    print(event)
    function = event['function']
    
    if function == 'search_logs_by_trace':
        trace_id = get_named_parameter(event, 'trace_id')
        from_ts = get_named_parameter(event, 'from_ts')
        to_ts = get_named_parameter(event, 'to_ts')
        service = get_named_parameter(event, 'service')
        env = get_named_parameter(event, 'env')
        
        result = search_logs_by_trace(trace_id, from_ts, to_ts, service, env)
    else:
        result = f"오류: 함수 '{function}'를 인식할 수 없습니다"

    response = populate_function_response(event, result)
    print(response)
    return response
