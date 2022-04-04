import cv2 as cv
import subprocess as sp

filePath = "D://server//videos"
inputFile = "city-night-cvber.mp4"
outputFile = "out.mp4"

def ffmpeg():
    """reference: https://github.com/kkroening/ffmpeg-python"""
    stream = ffmpeg.input(filePath + "//" + inputFile)
    stream = ffmpeg.hflip(stream)
    stream = ffmpeg.output(stream, filePath + "//" + outputFile)
    ffmpeg.run(stream)


def rtmp(rtmpUrl="rtmp://127.0.0.1:1935/live/home", camera_path=0):
    cap = cv.VideoCapture(camera_path)

    # Get video information
    fps = int(cap.get(cv.CAP_PROP_FPS))
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

    # ffmpeg command
    command = ['ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-vcodec','rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', "{}x{}".format(width, height),
            '-r', str(fps),
            '-i', '-',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'ultrafast',
            '-f', 'flv', 
            rtmpUrl]

    # 管道配置
    p = sp.Popen(command, stdin=sp.PIPE)

    # read webcamera
    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            print("Opening camera is failed")
            break

        # process frame
        # your code
        # process frame

        # write to pipe
        try:
            p.stdin.write(frame.tostring())
        except IOError as e:
            pass
        finally:
            continue


if __name__ == '__main__':
    rtmp()
    pass