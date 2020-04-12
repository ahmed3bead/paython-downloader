import sys
import urllib.error
import urllib.request
import urllib.response
import pafy
import os
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
from PyQt5.uic.properties import QtGui, QtCore

from overlay import *
import humanize

ui, _ = loadUiType('main.ui')


class MainApp(QMainWindow, ui):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.initUi()
        self.handelButtons()
        ## Youtube :- one video

        ## Youtube :- playlist

    def initUi(self):

        pass

    def handelButtons(self):
        self.pushButton_6.clicked.connect(self.download)
        self.pushButton_10.clicked.connect(self.handelBrowse)
        ## Youtube
        self.pushButton_5.clicked.connect(self.getVideoData)
        self.pushButton_9.clicked.connect(self.saveBrowse)
        self.pushButton_4.clicked.connect(self.downloadVideo)
        self.pushButton_8.clicked.connect(self.save_playlist_browse)
        self.pushButton_7.clicked.connect(self.download_playlist)

        pass

    def handelProgress(self, blockNum, blockSize, totalSize):
        readedData = blockNum * blockSize
        if totalSize > 0:
            downloadPercetage = readedData * 100 / totalSize
            self.progressBar.setValue(downloadPercetage)
            QApplication.processEvents()

        pass

    def handelBrowse(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        path = QFileDialog.getSaveFileName(self, caption='Save as', directory='.', filter='All Files(*.*)',
                                           initialFilter='', options=options)
        self.lineEdit_2.setText(str(path[0]))

    def download(self):
        url = self.lineEdit.text()
        pathToSave = self.lineEdit_2.text()

        if url == '':
            QMessageBox.warning(self, "Data Error", 'Please add valid Url')
            return
        elif pathToSave == '':
            QMessageBox.warning(self, "Data Error", 'Please add valid path to save')
            return
        else:
            try:
                urllib.request.urlretrieve(url, pathToSave, self.handelProgress)
            except urllib.error.URLError as e:
                QMessageBox.warning(self, "Download Error", e.reason)
                return
        QMessageBox.information(self, 'Download Completed', 'Download Completed')
        self.lineEdit.setText('')
        self.lineEdit_2.setText('')
        self.progressBar.setValue(0)

    ###################################
    ######### Youtube one video #######
    ###################################
    def saveBrowse(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        path = QFileDialog.getSaveFileName(self, caption='Save as', directory='.', filter='All Files(*.*)',
                                           initialFilter='', options=options)
        self.lineEdit_4.setText(str(path[0]))

    def getVideoData(self):

        videoLink = self.lineEdit_3.text()
        if (videoLink == ''):

            QMessageBox.warning(self, "Data Error",
                                "Please add valid Youtube URL like this 'https://www.youtube.com/watch?v=xxxxx'")
        else:
            try:
                data = pafy.new(videoLink)
                all_streams = data.videostreams
                for stream in all_streams:
                    size = humanize.naturalsize(stream.get_filesize())
                    data = "{} - {} - {} ".format(stream.extension, stream.quality, size)
                    self.comboBox.addItem(data)
            except Exception as error:
                QMessageBox.warning(self, 'Fetch Data Error', str(error))
                return

        pass

    def downloadVideo(self):
        video_link = self.lineEdit_3.text()
        save_path = self.lineEdit_4.text()

        if video_link == '':
            QMessageBox.warning(self, "Data Error",
                                "Please add valid Youtube URL like this 'https://www.youtube.com/watch?v=xxxxx'")
            return
        elif save_path == '':
            QMessageBox.warning(self, "Data Error", 'Please add valid path to save')
            return
        else:
            video = pafy.new(video_link)
            video_stream = video.videostreams
            video_quality = self.comboBox.currentIndex()
            try:
                download = video_stream[video_quality].download(filepath=save_path, callback=self.handel_video_progress)
                QMessageBox.information(self, 'Download Completed', 'Download Completed')
            except Exception as error:
                QMessageBox.warning(self, 'Download video Error', str(error))
                return
            self.lineEdit_3.setText('')
            self.lineEdit_4.setText('')
            self.progressBar_2.setValue(0)

    def handel_video_progress(self, total, recvd, ratio, rate, eta):
        readedData = recvd
        if total > 0:
            downloadPercetage = readedData * 100 / total
            self.progressBar_2.setValue(downloadPercetage)
            QApplication.processEvents()

    ##playlist

    def download_playlist(self):
        paylist_url = self.lineEdit_6.text()
        paylist_save_path = self.lineEdit_5.text()
        if paylist_url == '':
            QMessageBox.warning(self, "Data Error",
                                "Please add valid Playlist URL like this 'https://www.youtube.com/playlist?list=xxxxx'")
            return
        elif paylist_save_path == '':
            QMessageBox.warning(self, "Data Error", 'Please add valid path to save')
            return
        else:
            try:
                playlist = pafy.get_playlist(paylist_url)
                videos = playlist['items']
                self.lcdNumber_2.display(len(playlist['items']))
                os.chdir(paylist_save_path)
                if os.path.exists(str(playlist['title'])):
                    os.chdir(str(playlist['title']))
                else:
                    os.mkdir(str(playlist['title']))
                    os.chdir(str(playlist['title']))
                current_video_in_download = 1
                # quality = self.comboBox_2.currentIndex()
                QApplication.processEvents()

                for video in playlist['items']:
                    self.lcdNumber.display(current_video_in_download)
                    current_video = video['pafy'].getbest()
                    print(current_video)
                    playlist_meta = video['playlist_meta']
                    title = playlist_meta['title']
                    thumbnail = playlist_meta['thumbnail']
                    length_seconds = round(playlist_meta['length_seconds']/60, 2)
                    self.label_4.setText(str('Now Downloading {} Length {} '.format(title, length_seconds)))

                    download = current_video.download(callback=self.handel_playlist_progress)
                    current_video_in_download += 1
                    QApplication.processEvents()
            except Exception as error:
                QMessageBox.warning(self, 'Download video Error', str(error))
                return

    def handel_playlist_progress(self, total, recvd, ratio, rate, eta):
        readedData = recvd
        if total > 0:
            rate = humanize.naturalsize(rate)
            self.label_11.setText(str(' {} '.format(rate)))
            download_percentage = readedData * 100 / total
            self.progressBar_3.setValue(download_percentage)
            remaining_time = round(eta/60, 2)
            QApplication.processEvents()

    def save_playlist_browse(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontUseCustomDirectoryIcons
        dialog = QFileDialog()
        dialog.setOptions(options)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setDirectory('.')
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.exec_()
        path = dialog.selectedFiles()[0]
        self.lineEdit_5.setText(path)


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
