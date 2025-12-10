HLS streamer notes (using ffmpeg):

Example command to convert RTSP -> HLS segments for camera id 1:

docker run --rm --net host -v $(pwd)/hls:/tmp/hls jrottenberg/ffmpeg:4.3-alpine \

  -i "rtsp://user:pass@CAM_IP:554/stream" -c:v copy -hls_time 2 -hls_list_size 3 -hls_flags delete_segments /tmp/hls/1.m3u8


Then nginx (in docker-compose) serves /hls as /streams.

This is only a simple approach; for low-latency use WebRTC solutions.
