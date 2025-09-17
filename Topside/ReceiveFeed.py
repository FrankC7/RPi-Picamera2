import sys
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QThread, Signal, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

class VideoStreamThread(QThread):

    changePixmap = Signal(QPixmap)

    def __init__(self, url: QUrl):
        super().__init__()
        self.url = url
        self._run_flag = True
        self.manager = QNetworkAccessManager()
        self.reply: QNetworkReply = None
        self.buffer = b''
        self.boundary = b'--frame\r\n'
        #print(f"[{self.__class__.__name__}] Initialized for URL: {self.url.toString()}")

    def run(self):
        #print(f"[{self.__class__.__name__}] run() method started.")
        request = QNetworkRequest(self.url)
        self.reply = self.manager.get(request)
        self.reply.readyRead.connect(self.read_data)

        self.exec()
        #print(f"[{self.__class__.__name__}] Event loop finished.")
    
    def _handle_network_error(self, code: QNetworkReply.NetworkError):
        #print(f"[{self.__class__.__name__}] Network Error: {self.reply.errorString()}")
        self.stop()

    def _handle_finished(self):
        if self.reply.error() != QNetworkReply.NetworkError.OperationCanceledError:
            print(f"[{self.__class__.__name__}] Network reply finished. Error: {self.reply.errorString()}")
        self.stop()

    def read_data(self):
        data = self.reply.readAll().data()
        self.buffer += data

        while True:
            start_index = self.buffer.find(self.boundary)
            if start_index == -1:
                break

            header_end_index = self.buffer.find(b'\r\n\r\n', start_index + len(self.boundary))
            if header_end_index == -1:
                break

            frame_end_index = self.buffer.find(self.boundary, header_end_index + 4)
            if frame_end_index == -1:
                break

            jpeg_data_start = header_end_index + 4
            jpeg_data = self.buffer[jpeg_data_start : frame_end_index - 2]

            '''
            print(f"[{self.__class__.__name__}] --- Frame Extracted ---")
            print(f"Raw buffer part leading to this frame: {self.buffer[start_index : jpeg_data_start + 20]}")
            print(f"Extracted JPEG data length: {len(jpeg_data)}")
            print(f"JPEG data starts with: {jpeg_data[:20]}")
            print(f"JPEG data ends with: {jpeg_data[-20:]}")
            print(f"Buffer before processing frame starts: {self.buffer[:100]}. Length: {len(self.buffer)}")

            if not jpeg_data.startswith(b'\xff\xd8') or not jpeg_data.endswith(b'\xff\xd9'):
                print(f"[{self.__class__.__name__}] Warning: Extracted data does not resemble a JPEG")
            '''

            try:
                q_image = QImage.fromData(jpeg_data)
                if not q_image.isNull():
                    pixmap = QPixmap.fromImage(q_image)
                    self.changePixmap.emit(pixmap)
                else:
                    print(f"[{self.__class__.__name__}] Qt could not decode JPEG")
            except Exception as e:
                print(f"Error processing frame: {e}")

            self.buffer = self.buffer[frame_end_index:]
            #print(f"[{self.__class__.__name__}] Buffer after processing frame. Length: {len(self.buffer)}")
            

    def stop(self):
        print(f"[{self.__class__.__name__}] Stopping thread")
        self._run_flag = False
        if self.reply:
            #print(f"[{self.__class__.__name__}] Aborting network reply")
            self.reply.abort()
            self.reply.deleteLater()
        self.quit()
        self.wait(2000)
        if self.isRunning():
            print(f"[{self.__class__.__name__}] WARNING: Thread did not terminate correctly")
        else:
            print(f"[{self.__class__.__name__}] QThread stopped successfully.")
