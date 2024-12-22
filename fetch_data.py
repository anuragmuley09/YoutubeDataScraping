from googleapiclient.discovery import build
import pandas as pd
import time
import cred


MAX_RESULTS = 500 

# creating an youtube object with my API key
yt = build("youtube", "v3", developerKey=cred.my_key)

query = "Football Highlights"

def get_video_data(video_ids):
    '''
    i didnt had any idea about this earlier, 
    snippet: title, description, channel name
    statistic: view count
    contentDetails: video duration and format? 
    '''
    video_request = yt.videos().list( # fetching video data from this API endpoint
        part="snippet,statistics,contentDetails",
        id=",".join(video_ids)
    )

    video_response = video_request.execute()

    video_data = []
    for video in video_response["items"]:
        video_data.append({
            "Video Title": video["snippet"]["title"],
            "Video Link": "https://youtube.com/watch?v="+video['id'],
            "View Count": video["statistics"].get("viewCount", "N/A"),
            "Description": video["snippet"].get("description", "N/A"),
            "Channel Title": video["snippet"]["channelTitle"],
            "Tag": video["snippet"].get("tags", []),
            "Duration": video["contentDetails"].get("duration", "N/A"), # duration format PT#H#M#S
        })



    return video_data

def fetch_query_data(query):
    all_videos = [] # to store all the videos
    next_page_token = None # this is used to implemet pagination 

    while len(all_videos) < MAX_RESULTS:
        search_request = yt.search().list( #Fetching list of searhch reasults 
            part = "snippet",
            type="video",
            q=query,
            maxResults = 50,
            pageToken = next_page_token # handle pagination for results exceeding maxResults (50).
        )

        search_response = search_request.execute()

        """
        1. get all the video ids from the 
        2. get video data
        3. append it to the list
        """

        # 1
        video_ids = []
        for item in search_response["items"]:
            video_ids.append(item["id"]["videoId"])
        
        # 2
        video_data = get_video_data(video_ids)

        # 3
        all_videos.extend(video_data)


        # set next page token as we want data till MAX_RESULTS
        next_page_token = search_response.get("nextPageToken")
        if not next_page_token:
            break

        time.sleep(1)

    return all_videos


def main():

    
    video_data = fetch_query_data(query)
    df = pd.DataFrame(video_data)
    csv_file = f"{query}_top_500_videos.csv"
    df.to_csv(csv_file, index=False)
    print(f"Data saved to {csv_file}")

if __name__ == "__main__":
    main()