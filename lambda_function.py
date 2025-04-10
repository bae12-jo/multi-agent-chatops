import json
import boto3
import logging
from typing import List, Dict, Any, Union

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    """
    Bedrock Knowledge Base에서 Custom Chunking을 위한 Lambda 함수
    다양한 형식의 JSON 데이터를 처리합니다.
    """
    logger.debug(f'입력 이벤트: {json.dumps(event, default=str)[:500]}...')
    s3 = boto3.client('s3')

    # 입력 이벤트에서 필요한 정보 추출
    input_files = event.get('inputFiles')
    input_bucket = event.get('bucketName')
    
    if not input_files or not input_bucket:
        logger.error("필수 입력 파라미터 누락: inputFiles 또는 bucketName")
        return {"outputFiles": []}  # 오류 시 빈 결과 반환
    
    output_files = []
    
    for input_file in input_files:
        content_batches = input_file.get('contentBatches', [])
        file_metadata = input_file.get('fileMetadata', {})
        original_file_location = input_file.get('originalFileLocation', {})
        
        processed_batches = []
        
        for batch in content_batches:
            input_key = batch.get('key')
            
            if not input_key:
                logger.error("content batch에 key가 없음")
                continue
            
            try:
                # S3에서 파일 읽기
                file_content = read_s3_file(s3, input_bucket, input_key)
                
                # 파일 내용 처리 (청킹)
                chunked_content = process_content(file_content)
                
                # 출력 키 생성
                output_key = f"output/{input_key}"
                
                # 처리된 내용을 S3에 쓰기
                write_to_s3(s3, input_bucket, output_key, chunked_content)
                
                # 처리된 배치 정보 추가
                processed_batches.append({
                    'key': output_key
                })
            
            except Exception as e:
                logger.error(f"파일 처리 중 오류 발생: {str(e)}")
                # 오류가 발생해도 계속 진행
        
        # 출력 파일 정보 준비
        output_file = {
            'originalFileLocation': original_file_location,
            'fileMetadata': file_metadata,
            'contentBatches': processed_batches
        }
        output_files.append(output_file)
    
    result = {'outputFiles': output_files}
    logger.debug(f'반환 결과: {json.dumps(result, default=str)[:500]}...')
    
    return result

def read_s3_file(s3_client, bucket, key):
    """S3에서 파일을 읽어 JSON으로 파싱합니다."""
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except Exception as e:
        logger.error(f"S3 파일 읽기 오류 - 버킷: {bucket}, 키: {key}, 오류: {str(e)}")
        raise

def write_to_s3(s3_client, bucket, key, content):
    """JSON 내용을 S3에 씁니다."""
    try:
        s3_client.put_object(
            Bucket=bucket, 
            Key=key, 
            Body=json.dumps(content, ensure_ascii=False),
            ContentType='application/json'
        )
    except Exception as e:
        logger.error(f"S3 파일 쓰기 오류 - 버킷: {bucket}, 키: {key}, 오류: {str(e)}")
        raise

def process_content(file_content: dict) -> dict:
    """
    파일 내용을 처리하여 청크로 분할합니다.
    다양한 JSON 형식(배열, 객체)을 처리할 수 있습니다.
    """
    chunked_content = {
        'fileContents': []
    }
    
    # fileContents 필드가 없으면 빈 배열 기본값 사용
    file_contents = file_content.get('fileContents', [])
    
    for content in file_contents:
        content_body = content.get('contentBody', '')
        content_type = content.get('contentType', '')
        content_metadata = content.get('contentMetadata', {})
        
        # 내용이 없으면 건너뜀
        if not content_body:
            continue
            
        try:
            # JSON 문자열을 객체로 파싱
            json_data = parse_json_safely(content_body)
            
            # 데이터 형식 감지 및 처리
            chunks = chunk_json_data(json_data)
            
            # 각 청크를 fileContents에 추가
            for chunk in chunks:
                chunked_content['fileContents'].append({
                    'contentType': content_type,
                    'contentMetadata': content_metadata,
                    'contentBody': json.dumps(chunk, ensure_ascii=False)
                })
                
        except Exception as e:
            logger.error(f"콘텐츠 처리 중 오류: {str(e)}")
            # 원본 내용을 그대로 추가
            chunked_content['fileContents'].append({
                'contentType': content_type,
                'contentMetadata': content_metadata,
                'contentBody': content_body
            })
    
    return chunked_content

def parse_json_safely(json_str: str) -> Union[Dict, List, str]:
    """JSON 문자열을 안전하게 파싱합니다."""
    try:
        return json.loads(json_str) if isinstance(json_str, str) else json_str
    except Exception:
        # 이미 객체인 경우 그대로 반환
        return json_str

def chunk_json_data(data: Any) -> List[Any]:
    """
    JSON 데이터를 청크로 분할합니다.
    배열인 경우 각 항목을 청크로 처리하고,
    객체인 경우 각 키-값 쌍을 청크로 처리합니다.
    """
    chunks = []
    
    try:
        # 배열 형식 처리 (예: 오류 로그 목록)
        if isinstance(data, list):
            for item in data:
                chunks.append(item)
        
        # 객체 형식 처리 (예: 서비스별 담당자 정보)
        elif isinstance(data, dict):
            for key, value in data.items():
                # 객체에 서비스 ID를 추가하여 별도 청크로 생성
                if isinstance(value, dict):
                    service_chunk = {'service_id': key, **value}
                    chunks.append(service_chunk)
                else:
                    chunks.append({key: value})
        
        # 그 외 데이터 형식은 그대로 하나의 청크로 처리
        else:
            chunks.append(data)
            
    except Exception as e:
        logger.error(f"JSON 데이터 청킹 중 오류: {str(e)}")
        # 오류 발생 시 원본 데이터를 그대로 사용
        chunks.append(data)
    
    return chunks if chunks else [data]  # 청크가 없으면 원본 데이터 반환