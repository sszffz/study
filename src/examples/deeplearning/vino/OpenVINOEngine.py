from abc import ABC, abstractclassmethod
import numpy as np
import cv2 as cv
from openvino.inference_engine import IECore

class OpenVINOEngine(ABC):
    
    def __init__(self, model_xml: str, model_bin: str, ie: IECore) -> None:
        self._model_xml = model_xml
        self._model_bin = model_bin
        self._net = ie.read_network(model=model_xml, weights=model_bin)
        self._exec_net = ie.load_network(network=self._net, device_name='CPU')

    @staticmethod
    def _resize_cv_image(cv_image: np.ndarray, final_width: int, final_height: int):
        image = cv.resize(cv_image, (final_width, final_height))
        return image.transpose(2, 0, 1)

    @abstractclassmethod
    def infer(self, cv_frame: np.ndarray):
        pass        