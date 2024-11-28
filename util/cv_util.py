import cv2
import random
import numpy as np


def img_crop(frame, position, resizer=0):
    try:
        croped = frame[position[1]:position[1] + position[3], position[0]:position[0] + position[2]]
        if resizer == 0:
            return croped
        return cv2.resize(croped, dsize=(0, 0), fx=resizer, fy=resizer, interpolation=cv2.INTER_LINEAR)

    except Exception as e:
        print(f"cvutil img_crop error ({e})")


def extract_whole_frame(vedio_file) -> list:
    """
    - 비디오 파일로 전체 프레임 추출
    - return frame_list
    """
    frames = []
    try:
        cap = cv2.VideoCapture(tsfile)
        if not cap.isOpened(): return []

        while True:
            ret, cur_frame = cap.read()
            if not ret: break
            frames.append(cur_frame)
        cap.release()
        return frames

    except Exception as e:
        print(f"extract_whole_frame failed ({e})")
        return []


def extract_side_frames(tsfile) -> list:
    """
    - ts 파일로 부터 맨 첫장과 마지막 프레임 추출
    - return frame_list
    """
    frames = []
    try:
        cap = cv2.VideoCapture(tsfile)
        if not cap.isOpened(): return []
        # frame 개수가 2보다 작으면
        if int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) < 2:
            return []

        while True:
            ret, cur_frame = cap.read()
            if not ret: break
            frames.append(cur_frame)
        cap.release()

        return [frames[0], frames[-1]]

    except Exception as e:
        print(f"extract_whole_frame failed ({e})")
        return []


def extract_frames(tsfile, frame_count=1) -> (list, any):
    """
    - ts 파일로 부터 이미지 프레임 추출
    - 기본으로 1개의 프레임 추출
    - return frame_list, frameIndex_list
    """
    try:
        cap = cv2.VideoCapture(tsfile)
        if cap.isOpened() == False:
            print(f"{tsfile} open fail.")
            return [], None

        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frames = []
        stride = int(total / (frame_count - 1)) - 1
        indexes = list(range(0, total, stride))
        indexes.append(total - 1)

        for x in range(total):
            ret, frame = cap.read()
            if ret == False:
                break

            if x in indexes:
                frames.append(frame)

            if len(frames) == len(indexes):
                break

        cap.release()
        return frames, indexes
    except Exception as e:
        print(f"extract_frames ERROR (reason : {e})")
        return [], []


def extract_frames_from_mp4(mp4file, frame_count_per_sec=1) -> (list, any):
    """
    - mp4 파일로 부터 이미지 프레임 추출
    - 기본 1초당 1개의 프레임 추출
    - return frame_list, frameIndex_list
    """
    try:
        cap = cv2.VideoCapture(mp4file)
        if cap.isOpened() == False:
            print(f"{mp4file} open fail.")
            return [], None

        frames = []
        indexes = []

        frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
        frame_interval = frame_rate // frame_count_per_sec
        current_time = 0

        while True:
            ret, frame = cap.read()
            if not ret: break
            if current_time % frame_interval == 0:
                frames.append(frame)
                indexes.apeend(current_time)
            current_time += 1

        cap.release()
        return frames, indexes
    except Exception as e:
        print(f"extract_frames_from_mp4 ERROR (reason : {e})")
        return [], []


def extract_frame(tsfile):
    """
    - ts 파일로 부터 이미지 프레임 추출
    - return frame (실패시 None)
    """
    try:
        cap = cv2.VideoCapture(tsfile)
        if cap.isOpened() == False:
            print(f"{tsfile} open fail.")
            return None

        ret, frame = cap.read()
        if ret == False: return None
        cap.release()
        return frame
    except Exception as e:
        print(f"{tsfile} extract_frame failed (reason:{e})")
        return None


def draw(frame, pos, w, h, color=None):
    if color == 'red':
        RGB = (0, 0, 255)
    elif color == 'green':
        RGB = (0, 255, 0)
    elif color == 'blue':
        RGB = (255, 0, 0)
    elif color == 'white':  # white
        RGB = (255, 255, 255)
    elif color == 'test1':
        RGB = (175, 0, 175)
    elif color == 'test2':
        RGB = (175, 175, 0)
    elif color == 'test3':
        RGB = (50, 50, 50)
    else:
        RGB = (0, 255, 255)
    return cv2.rectangle(frame, pos, (pos[0] + w, pos[1] + h), RGB, 3)


def sharpen_image(image):
    '''
    샤프닝(sharpening)
    - 영상을 날카롭게 만드는 처리
    - 영상을 선명하게 할 때 사용
    - 중심 화소값과 인접 화소값의 차이를 더 크게 만듬
    '''
    try:
        src = image.copy()
        mask = np.asarray([[-1, -1, -1],
                           [-1, 9, -1],
                           [-1, -1, -1]], dtype=np.float32)
        sharpening_img = cv2.filter2D(src, -1, mask)
        return sharpening_img
    except Exception as e:
        print(f"cvutil sharpen_image error ({e})")
        return None
