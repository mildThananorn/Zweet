from googleapiclient.discovery import build
from datetime import datetime
import pandas as pd

def get_video_details(youtube, video_ids):
    all_video_stats = []
    
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(video_ids[i:i+50])
        )
        response = request.execute()
        
        for video in response['items']:
            video_stats = {
                'วิดีโอไอดี': video['id'],
                'ชื่อวิดีโอ': video['snippet']['title'],
                'วันที่อัพโหลด': datetime.strptime(video['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d'),
                'ระยะเวลา': video['contentDetails']['duration'],
                'ยอดวิว': int(video['statistics'].get('viewCount', 0)),
                'ไลค์': int(video['statistics'].get('likeCount', 0)),
                'ความคิดเห็น': int(video['statistics'].get('commentCount', 0)),
                'รายการโปรด': int(video['statistics'].get('favoriteCount', 0)),
                'คำอธิบาย': video['snippet']['description'],
                'แท็ก': ', '.join(video['snippet'].get('tags', [])),
                'หมวดหมู่ไอดี': video['snippet']['categoryId'],
                'ภาษา': video['snippet'].get('defaultLanguage', ''),  
                'ประเทศ': video['snippet'].get('defaultAudioLanguage', '')  
            }
            all_video_stats.append(video_stats)
            
    return all_video_stats

def get_all_channel_videos(youtube, channel_id):
    """ดึงรายการวิดีโอทั้งหมดของช่อง"""
    video_ids = []
    
    request = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    )
    response = request.execute()
    playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    

    next_page_token = None
    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        
        for item in response['items']:
            video_ids.append(item['snippet']['resourceId']['videoId'])
            
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    
    return video_ids

def main():

    api_key = 'YOUR_API_KEY'
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    channel_id = 'TARGET_CHANNEL_ID'
    
    try:
        print("กำลังดึงรายการวิดีโอ...")
        video_ids = get_all_channel_videos(youtube, channel_id)
        print(f"พบวิดีโอทั้งหมด {len(video_ids)} รายการ")
        
        print("กำลังดึงข้อมูลวิดีโอ...")
        video_data = get_video_details(youtube, video_ids)
        
        df = pd.DataFrame(video_data)
        excel_filename = 'youtube_videos_data.xlsx'
        df.to_excel(excel_filename, index=False, engine='openpyxl')
        print(f"บันทึกข้อมูลลงไฟล์ {excel_filename} เรียบร้อยแล้ว")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {str(e)}")

if __name__ == "__main__":
    main()