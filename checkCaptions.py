from googleapiclient.discovery import build
import pandas as pd
import time
import cred

MAX_RESULTS = 50  # Further reduced to save quota

yt = build("youtube", "v3", developerKey=cred.my_key)

def get_captions_metadata(video_id):
    try:
        # Fetch caption metadata
        caption_request = yt.captions().list(
            part="snippet",
            videoId=video_id
        )
        caption_response = caption_request.execute()

        if "items" in caption_response and caption_response["items"]:
            captions = [
                f"{item['snippet']['language']} - {item['snippet']['name']}"
                for item in caption_response["items"]
            ]
            return "; ".join(captions)  # Combine all available captions
        else:
            return "N/A"
    except Exception as e:
        print(f"Error fetching captions for video ID {video_id}: {e}")
        return "N/A"

def get_video_data(video_ids):
    video_request = yt.videos().list(
        part="snippet,statistics,contentDetails",
        id=",".join(video_ids)
    )
    video_response = video_request.execute()

    video_data = []
    for video in video_response["items"]:
        # Fetch captions metadata
        captions = get_captions_metadata(video["id"])

        video_data.append({
            "Video Title": video["snippet"]["title"],
            "Video Link": f"https://youtube.com/watch?v={video['id']}",
            "View Count": video["statistics"].get("viewCount", "N/A"),
            "Description": video["snippet"].get("description", "N/A"),
            "Channel Title": video["snippet"]["channelTitle"],
            "Tag": video["snippet"].get("tags", []),
            "Duration": video["contentDetails"].get("duration", "N/A"),
            "Comment Count": video["statistics"].get("commentCount", "N/A"),
            "Publish Date": video["snippet"]["publishedAt"],
            "Captions": captions,  # Save captions metadata
        })

    return video_data

def fetch_query_data(query):
    all_videos = []
    next_page_token = None

    while len(all_videos) < MAX_RESULTS:
        search_request = yt.search().list(
            part="snippet",
            type="video",
            q=query,
            maxResults=50,
            pageToken=next_page_token,
            videoCaption="closedCaption"  # Only fetch videos with captions
        )
        search_response = search_request.execute()

        video_ids = [item["id"]["videoId"] for item in search_response["items"]]
        video_data = get_video_data(video_ids)
        all_videos.extend(video_data)

        next_page_token = search_response.get("nextPageToken")
        if not next_page_token:
            break

        time.sleep(1)

    return all_videos

def main():
    query = input("Enter Genre: ")
    video_data = fetch_query_data(query)
    df = pd.DataFrame(video_data)
    csv_file = f"data/{query}_top_{MAX_RESULTS}_videos.csv"
    df.to_csv(csv_file, index=False)
    print(f"Data saved to {csv_file}")

if __name__ == "__main__":
    main()
