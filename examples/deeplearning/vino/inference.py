import os
import time
import cv2 as cv
from openvino.inference_engine import IECore

from FaceDetection import FaceDetection, FaceDetectionModel
from EmotionRecognition import EmotionRecognition

def list_supported_devices(ie: IECore):
    for device in ie.available_devices:
        print(device)


def _main():
    os.chdir(os.path.dirname(__file__))
    ie = IECore()
    list_supported_devices(ie)

    face_detection_engine = FaceDetection.get_network(FaceDetectionModel.MODEL_0200, ie)
    # face_detection_engine = FaceDetection.get_network(FaceDetectionModel.MODEL_0206, ie)

    emotion_recognition_engine = EmotionRecognition.get_network(ie)
    face_detection_engine.register_proc_engine(emotion_recognition_engine)

    cap = cv.VideoCapture(0)
    cv.namedWindow("frame")

    while True:
        ret, frame = cap.read()
        if ret is not True:
            break
            
        face_detection_engine.infer(frame)
        cv.imshow("frame", frame)
        key = cv.waitKey(1)
        if key == 27:
            break

    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    _main()
