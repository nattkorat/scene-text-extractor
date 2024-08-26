import sys
import cv2
import requests
from PyQt5.QtCore import QTimer, Qt, QRect, QPoint
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtWidgets import *


import style

class CameraApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.start_pos = None
        self.end_pos = None

        # Set up the window
        self.setWindowTitle("Scene Text Selection")
        self.setFixedSize(900, 500)

        # Set up the central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        self.timer = QTimer(self)
        self.video_label = QLabel(self)
        self.lb_camera = QLabel("Camera View")
        self.btn_came = QPushButton("Camera")
        self.lb_select = QLabel("Selected Preview")
        self.select_img = QLabel(self)
        self.result_text = QLabel("Result")

        self.col1 = QVBoxLayout()
        self.col2 = QVBoxLayout()
        self.row_layout = QHBoxLayout()

        self.layout.addLayout(self.col1, stretch=3)
        self.layout.addLayout(self.col2, stretch=1)
        self.col1.addWidget(self.lb_camera, alignment=Qt.AlignTop)
        self.col1.addWidget(self.video_label, stretch=1)
        self.row_layout.addWidget(self.btn_came, alignment=Qt.AlignHCenter)

        self.col1.addLayout(self.row_layout)

        self.col2.addWidget(self.lb_select, alignment=Qt.AlignTop)
        self.col2.addWidget(self.select_img, stretch=1)
        self.col2.addWidget(self.result_text, stretch=2)

        self.btn_came.clicked.connect(self.camera_handle)
        

        # Start the timer to update the frame
        self.timer.start(60)
        self.setup_style()
    
    def setup_style(self):
        self.btn_came.setStyleSheet(style.button("blue"))
        self.select_img.setStyleSheet(style.border())
        self.result_text.setStyleSheet("qproperty-alignment: AlignCenter;")
        self.video_label.setStyleSheet("background-color: dark-gray; border-radius: 10px;")
    

    def camera_handle(self):
        if self.btn_came.text() == "Camera":
            self.btn_came.setText("Stop")
            self.btn_came.setStyleSheet(style.button("red"))
            self.start_came()
        else:
            self.btn_came.setText("Camera")
            self.btn_came.setStyleSheet(style.button("blue"))
            self.close_came()
    

    def start_came(self):
        self.timer.timeout.connect(self.update_frame)
        self.cap = cv2.VideoCapture(0)
    

    def close_came(self):
        self.cap.release()
        self.video_label.clear()


    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # rgb_frame = cv2.flip(rgb_frame, 1)

            # Convert the frame to QImage
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            img = QPixmap.fromImage(qimg)
            w, h = self.video_label.width(), self.video_label.height()

            self.pixmapimage = img.scaled(w, h, Qt.KeepAspectRatio)
            self.video_label.setPixmap(self.pixmapimage)


    def closeEvent(self, event):
        # Release the camera when the window is closed
        self.cap.release()
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.validate_pos(event.pos()):
            print(event.pos())
            self.start_pos = self.update_point(event.pos())
    
    def mouseMoveEvent(self, event):
        if self.validate_pos(event.pos()):
            print(event.pos())     
            self.end_pos = self.update_point(event.pos())
            self.drawBoundingBox()
    
    def mouseReleaseEvent(self, event):
        if self.validate_pos(event.pos()):
            print(f"Mouse release {event.pos()}")
            self.drawBoundingBox()
            self.getSelectedArea()
            result = self.get_inf()
            if result:
                text = result.get("result", None)
                self.result_text.setText(text)


    def drawBoundingBox(self):
        if self.btn_came.text() == "Stop":
            self.image = self.pixmapimage.copy()

            if self.start_pos and self.end_pos:
                painter = QPainter(self.image)
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                rect = QRect(self.start_pos, self.end_pos)
                painter.drawRect(rect)
                painter.end()
            
            self.video_label.setPixmap(self.image)

    
    def validate_pos(self, pos):
        is_cam = self.btn_came.text() == "Stop"
        return is_cam and self.video_label.rect().contains(pos)
    
    def update_point(self, pos):
        vy = self.video_label.pos().y()
        print(f"========={vy}=======")
        x, y = pos.x(), pos.y()

        # need to adjust for the screen
        return QPoint(x - 15, y - 60)
    
    def getSelectedArea(self):
        self.cropped_img = self.pixmapimage.copy(self.getBoundingBox())
        self.cropped_img.save("temp.png", "PNG")
        w, h = self.select_img.width(), self.select_img.height()
        self.cropped_img = self.cropped_img.scaled(w, h, Qt.KeepAspectRatio)

        self.select_img.setPixmap(self.cropped_img)
    
    def getBoundingBox(self):
        return QRect(self.start_pos, self.end_pos)
    
    def get_inf(self):
        try:
            response = requests.post(
                url=" http://10.5.5.50:5000/api/ocr/eng",
                files={
                        "media": open("temp.png", "rb")
                },
                timeout=5
            )
            return response.json()
        
        except Exception as error:
            return None
        

    
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())
