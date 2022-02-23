from __future__ import annotations

import numpy as np
import cv2 as cv

from openvino.inference_engine import IECore
from OpenVINOEngine import OpenVINOEngine

class EmotionRecognition(OpenVINOEngine):

    emotions = ['neutral', 'happy', 'sad', 'surprise', 'angry']

    def __init__(self, model_xml: str, model_bin: str, ie: IECore) -> None:
        super().__init__(model_xml, model_bin, ie)

        self._input_tensor_name = 'data'
        self._output_tensor_name = 'prob_emotion'
        self._input_height = 64
        self._input_width = 64

    def infer(self, cv_frame: np.ndarray):
        image = OpenVINOEngine._resize_cv_image(cv_frame, self._input_width, self._input_height)
        res = self._exec_net.infer(inputs={self._input_tensor_name:[image]})
        res = res[self._output_tensor_name]
        emotion_prob = res.reshape(1, 5)
        label_index = int(np.argmax(emotion_prob, 1))
        return EmotionRecognition.emotions[label_index]

    @staticmethod
    def get_network(ie: IECore) -> EmotionRecognition:
        return EmotionRecognition('./models/emotion-recognition/emotions-recognition-retail-0003.xml',
                                  './models/emotion-recognition/emotions-recognition-retail-0003.bin',
                                  ie)