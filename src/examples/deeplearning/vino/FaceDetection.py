from __future__ import annotations
import time
from abc import ABC, abstractclassmethod
from enum import Enum
from collections import namedtuple
from typing import List

import numpy as np
import cv2 as cv
from openvino.inference_engine import IECore

from OpenVINOEngine import OpenVINOEngine

class FaceDetection(OpenVINOEngine):

    def __init__(self, model_xml: str, model_bin: str, ie: IECore) -> None:
        super().__init__(model_xml, model_bin, ie)
        self._face_proc_engine_list = []

    def get_infer_result(self, cv_frame: np.ndarray):
        image = OpenVINOEngine._resize_cv_image(cv_frame, self._input_width, self._input_height)

        inf_start = time.time()
        res = self._exec_net.infer(inputs={self.get_input_tensor_name():[image]})
        inf_duration = (time.time() - inf_start) * 1000
        print("infer duration (ms): {:.3f}".format(inf_duration))

        return res, inf_duration

    def register_proc_engine(self, engine: OpenVINOEngine):
        if engine not in self._face_proc_engine_list:
            self._face_proc_engine_list.append(engine)

    def _get_roi(self, frame: np.ndarray, box: tuple):
        xmin, ymin, xmax, ymax = box
        return frame[ymin:ymax, xmin:xmax, :]

    def _proc_individaul_face(self, cv_frame: np.ndarray, box: tuple, duration: float):
        roi = self._get_roi(cv_frame, box)
        result = self._face_inference(roi)
        xmin, ymin, xmax, ymax = box
        cv.rectangle(cv_frame, (xmin, ymin), (xmax, ymax), (0, 255, 255), 2, 8)
        cv.putText(cv_frame, "infer time (ms): {:.3f}".format(duration), (0, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255))
        cv.putText(cv_frame, result, (xmin, ymin-5), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255))

    def _face_inference(self, roi: np.ndarray):
        result_list = []
        for face_proc_engine in self._face_proc_engine_list:
            res = face_proc_engine.infer(roi)
            result_list.append(str(res))
        return " ".join(result_list)

    def infer(self, cv_frame: np.ndarray):
        res, duration = self.get_infer_result(cv_frame)
        boxes = self.get_face_boxes(cv_frame, res)
        for box in boxes:
            self._proc_individaul_face(cv_frame, box, duration)

    @abstractclassmethod
    def get_input_tensor_name(self) -> str:
        pass

    @abstractclassmethod
    def get_face_boxes(self, cv_frame: np.ndarray, face_detection_result) -> List:
        pass

    @staticmethod
    def get_network(model_type: FaceDetectionModel, ie: IECore) -> FaceDetection:
        return model_type.value.cls(model_type.value.xml, model_type.value.bin, ie)

class FaceDetection0200(FaceDetection):

    def __init__(self, model_xml: str, model_bin: str, ie: IECore) -> None:
        super().__init__(model_xml, model_bin, ie)

        self._input_tensor_name = 'image'
        self._output_tensor_name = 'detection_out'
        self._input_height = 256
        self._input_width = 256

    def get_input_tensor_name(self) -> str:
        return self._input_tensor_name

    def get_face_boxes(self, cv_frame: np.ndarray, face_detection_result) -> List:
        res = face_detection_result[self._output_tensor_name]
        ih, iw, _ = cv_frame.shape
        boxes = []
        for obj in res[0][0]:
            confidence = obj[2]
            if confidence > 0.5:
                rel_box = obj[3:7]
                xmin = max(int(rel_box[0] * iw), 0)
                ymin = max(int(rel_box[1] * ih), 0)
                xmax = min(int(rel_box[2] * iw), iw-1)
                ymax = min(int(rel_box[3] * ih), ih-1)
                boxes.append((xmin, ymin, xmax, ymax))
        return boxes


class FaceDetection0206(FaceDetection):

    def __init__(self, model_xml: str, model_bin: str, ie: IECore) -> None:
        super().__init__(model_xml, model_bin, ie)
        self._input_tensor_name = 'image'
        self._output_confidence_tensor_name = 'TopK_2434.0'
        self._output_box_tensor_name = 'boxes'
        self._input_height = 640
        self._input_width = 640

    def get_input_tensor_name(self) -> str:
        return self._input_tensor_name

    def get_face_boxes(self, cv_frame: np.ndarray, face_detection_result) -> List:
        confidences = face_detection_result[self._output_confidence_tensor_name]
        boxes = face_detection_result[self._output_box_tensor_name]
        ih, iw, ic = cv_frame.shape
        boxes = []
        for confidence, box in zip(confidences, boxes):
            if confidence > 0.5:
                xmin = max(int(box[0] * iw / self._input_width), 0)
                ymin = max(int(box[1] * ih / self._input_height), 0)
                xmax = min(int(box[2] * iw / self._input_width), iw-1)
                ymax = min(int(box[3] * ih / self._input_height), ih-1)
                boxes.append((xmin, ymin, xmax, ymax))
        return boxes


FaceDetectionModelInfo = namedtuple('FaceDetectionModelInfo', 'id cls xml bin')

class FaceDetectionModel(Enum):
    MODEL_0200 = FaceDetectionModelInfo(1, 
                                        FaceDetection0200,
                                        './models/face-detection/face-detection-0200.xml',
                                        './models/face-detection/face-detection-0200.bin')
    MODEL_0206 = FaceDetectionModelInfo(2, 
                                        FaceDetection0206,
                                        './models/face-detection/face-detection-0206.xml',
                                        './models/face-detection/face-detection-0206.bin')
