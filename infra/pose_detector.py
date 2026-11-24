"""Adaptador para o detector MediaPipe Pose."""


class PoseDetector:
    def __enter__(self):
        import mediapipe as mp

        if not hasattr(mp, "solutions"):
            raise RuntimeError(
                "API Pose indisponível. "
                "Instale as versões do requirements.txt."
            )

        self.pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        return self

    def detectar(self, frame):
        import cv2

        imagem_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        resultado = self.pose.process(imagem_rgb)

        if resultado.pose_landmarks is None:
            return None

        return resultado.pose_landmarks.landmark

    def __exit__(self, tipo, valor, traceback):
        self.pose.close()