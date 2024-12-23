from googleapiclient.discovery import build
import pandas as pd
import time
import cred

'''
Quota Excedded - test caption functionality 
'''

MAX_RESULTS = 500 

# creating an youtube object with my API key
yt = build("youtube", "v3", developerKey=cred.my_key)


# if captoions are available then fetch else, say N/A
def get_captions(video_id):
    try:
        caption_request = yt.captions().list(
            part="snippet",
            videoId = video_id
        )
        caption_response = caption_request.execute()

        if "items" in caption_response and caption_response["items"]:
            # get caption id
            caption_id = caption_response["items"][0]["id"] # whatever the first caption maybe, extract its id

            # download captions
            get_caption_request = yt.captions().download(
                id=caption_id,
                tfmt="srt" # Format SRT (SubRip Subtitle)
            ) 

            actual_caption = get_caption_request.execute()
            return actual_caption
        else:
            return "N/A" # no captions


    except Exception as e:
        print(f"Exception caused during caption fetching for video id: {video_id}")
        return "N/A"


def get_video_data(video_ids):
    ''' 
    snippet: title, description, channel name...
    statistic: view count...
    contentDetails: video duration and format? 
    '''
    video_request = yt.videos().list( # fetching video data from this API endpoint
        part="snippet,statistics,contentDetails",
        id=",".join(video_ids)
    )

    video_response = video_request.execute()

    video_data = []
    for video in video_response["items"]:
        captions = get_captions(video["id"])
        video_data.append({
            "Video Title": video["snippet"]["title"],
            "Video Link": "https://youtube.com/watch?v="+video['id'],
            "View Count": video["statistics"].get("viewCount", "N/A"),
            "Description": video["snippet"].get("description", "N/A"),
            "Channel Title": video["snippet"]["channelTitle"],
            "Tag": video["snippet"].get("tags", []),
            "Duration": video["contentDetails"].get("duration", "N/A"), # duration format PT#H#M#S
            "Comment Count": video["statistics"].get("commentCount", "N/A"),
            "Publish Date": video["snippet"]["publishedAt"],
            "Captions":  captions,
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
            maxResults = 100, # we can adjust this
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
        # basically this implements pagination
        next_page_token = search_response.get("nextPageToken")
        if not next_page_token:
            break

        time.sleep(1)

    return all_videos


def main():
    query = input("Enter Genre: ") # genre or any other search like "top BGT moments" anything 
    
    video_data = fetch_query_data(query)
    df = pd.DataFrame(video_data)
    csv_file = f"data/{query}_top_500_videos.csv"
    df.to_csv(csv_file, index=False)
    print(f"Data saved to {csv_file}")

if __name__ == "__main__":
    main()