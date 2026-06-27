import json
import os
import boto3
import urllib.request
from datetime import datetime

def lambda_handler(event, context):
    
    api_key = os.environ['YOUTUBE_API_KEY']
    bucket_name = os.environ['S3_BUCKET_NAME']
    region_name = os.environ['AWS_REGION_NAME']
    
    regions = ['IN', 'US', 'GB']
    all_data = []
    
    for region in regions:
        url = (
            f"https://www.googleapis.com/youtube/v3/videos"
            f"?part=snippet,statistics,contentDetails"
            f"&chart=mostPopular"
            f"&regionCode={region}"
            f"&maxResults=50"
            f"&key={api_key}"
        )
        
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
        for item in data.get('items', []):
            item['region_code'] = region
            item['ingested_at'] = datetime.utcnow().isoformat()
            all_data.append(item)
    
    now = datetime.utcnow()
    s3_key = (
        f"bronze/youtube_trending/"
        f"year={now.year}/month={now.month:02d}/"
        f"day={now.day:02d}/"
        f"trending_{now.strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    s3_client = boto3.client('s3', region_name=region_name)
    s3_client.put_object(
        Bucket=bucket_name,
        Key=s3_key,
        Body=json.dumps(all_data, indent=2),
        ContentType='application/json'
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Success',
            'records_ingested': len(all_data),
            's3_key': s3_key
        })
    }