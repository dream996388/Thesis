from Defect_Inspection.Imgp import ImageProcessing
from GC.GlassCaptures import GlassCaptures
from IO.PLC import PLC
from UI.MenuSetting import MenuSetting
from UI.MenuTeach import MenuTeach
from ui_functions import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow)
from Tools.log import *
from BaslerCAM.CAMS import CAMS
from linelight import LineLight
from ui_main import Ui_MainWindow
LAB_USED=1

class AOI_Window(Ui_MainWindow,QMainWindow):
    def __init__(self):
        super(AOI_Window, self).__init__()
        self.setupUi(self)

class AOI_sys(AOI_Window, QMainWindow):
    def __init__(self):
        super(AOI_sys, self).__init__()
        self.Is_connected=False
        self.ui_init()

        # new
        self.cams = CAMS(self)
        self.glassCaptures=GlassCaptures()
        self.linelight=LineLight(self)
        self.imgp=ImageProcessing(self)
        self.plc=PLC(self)
        # new

        self.menuTeach=MenuTeach(self)
        self.menuTeach.connect_signals()
        self.menuSetting=MenuSetting(self,self.cams,self.plc,self.linelight)
        self.menuSetting.connect_signals()
        self.menuCam_init()

        # check disk info
        # show_disk_info()


        # 主線程 執行計數器
        self.sys_timer=QTimer()
        self.sys_timer.setInterval(1000)
        self.sys_timer.timeout.connect(self.update_sys_time)
        self.sys_timer.start()
        
    def ui_init(self):
        self.UI_alarm = None
        self.UI_SetupLog()
        self.Save_TeachParas_pushButton.setStyleSheet("QPushButton {border: 2px solid rgb(52, 59, 72);border-radius: 5px;background-color: gray;\
                                                                                    }QPushButton:hover {background-color: rgb(57, 65, 80);border: 2px solid rgb(61, 70, 86);}\
                                                                                    QPushButton:pressed {background-color: rgb(35, 40, 49);border: 2px solid rgb(43, 50, 61);}")
        self.Save_TeachParas_pushButton.setEnabled(False)
        # UIFunctions
        UIFunctions.removeTitleBar(True)
        self.setWindowTitle('ODF AK_Glass Detect')
        UIFunctions.labelTitle(self, 'ODF AK_Glass Detect')
        startSize = QSize(1920, 1080)
        self.resize(startSize)
        self.setMinimumSize(startSize)
        # self.btn_toggle_menu.clicked.connect(lambda: UIFunctions.toggleMenu(self, 220, True))
        self.stackedWidget.setMinimumWidth(20)
        UIFunctions.addNewMenu(self, "Camera", "btn_camera", "url(:/16x16/icons/16x16/cil-camera.png)", True)
        UIFunctions.addNewMenu(self, "Line Light", "btn_linelight", "url(:/16x16/icons/16x16/cil-highligt.png)", True)
        UIFunctions.addNewMenu(self, "Teach", "btn_teach", "url(:/16x16/icons/16x16/cil-image1.png)", True)
        UIFunctions.addNewMenu(self, "Setting", "btn_settings", "url(:/16x16/icons/16x16/cil-settings.png)", True)
        UIFunctions.selectStandardMenu(self, "btn_camera")
        self.stackedWidget.setCurrentWidget(self.page_camera)
        UIFunctions.userIcon(self, "AUO", "", True)

        def moveWindow(event):
            if UIFunctions.returStatus(self) == 1:
                UIFunctions.maximize_restore(self)
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        self.frame_label_top_btns.mouseMoveEvent = moveWindow
        UIFunctions.uiDefinitions(self)
        # self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # setup linelight ui init
        self.LineLight_spinBox.setEnabled(False)
        self.LineLightClose_pushButton.setEnabled(False)
        self.LineLightOpen_pushButton.setEnabled(False)

        # setup cams ui init
        self.Exposure_doubleSpinBox.setKeyboardTracking(False)
        self.LineLight_spinBox.setKeyboardTracking(False)
        self.Height_spinBox.setKeyboardTracking(False)

        self.show()

    def menuCam_init(self):
        # cam ui event bind
        self.connectAll_btn_pressed = False
        self.ConnectAll_pushButton.clicked.connect(self.connectAll)
        self.OneShot_pushButton.clicked.connect(self.start_single)
        self.Stop_pushButton.clicked.connect(self.sys_stop)


    def update_sys_time(self):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        self.nowtime_label.setText(dt_string)
        # 更新硬碟剩餘容量
        # import shutil
        # total, used, free = shutil.disk_usage('C:/')
        #
        # total = total // (2 ** 30)
        # used = used // (2 ** 30)
        # self.Space_progressBar.setValue(int(used / total * 100))
        #
        # if used >= 1700:
        #     print('space clear')
        #     # show_disk_info()
        #     path2 = r"C:\1102-1103\1103\1103-cap\data\img"
        #
        #     list2 = os.listdir(path2)
        #
        #     try:
        #         for i in range(10):
        #             # path = os.path.join(path2, list2[i])
        #             print(path2 + f"//{list2[i]}")
        #             shutil.rmtree(path2 + f"//{list2[i]}")
        #     except:
        #         print('delete disk file error')
        if self.glassCaptures.left_worker is not None:
            gls_cnt = self.glassCaptures.left_worker.get_gls_cnt()
            self.detect_label.setText(str(gls_cnt - 1))

    def UI_SetupLog(self):
        file_name = datetime.now().strftime('OpenTime%Y-%m-%d-%H-%M-%S') + '.log'
        log_folder_path = os.path.join(os.getcwd(), 'log')
        if os.path.isdir(os.path.join(os.getcwd(), 'log')) is False:
            os.mkdir(log_folder_path)

        sys.stdout = Logger(file_name, log_folder_path, self.log_textBrowser)
        sys.stdout.log_UI = self.log_textBrowser
        sys.stdout.Signal.connect(self.Log_Action)
        print("Open Program")

    def Log_Action(self, text):
        if self.log_textBrowser.document().lineCount() > 100:
            self.log_textBrowser.clear()
        self.log_textBrowser.append(text)
        self.log_textBrowser.moveCursor(QTextCursor.End)


    def sys_stop(self):

        self.cams.stop()
        self.linelight.stop()
        self.glassCaptures.stop()

        self.staue_label.setText("閒置")
        self.OneShot_pushButton.setEnabled(True)
        self.OneShot_pushButton.setStyleSheet("QPushButton {border: 2px solid rgb(52, 59, 72);border-radius: 5px;background-color: rgb(52, 59, 72);\
                                                        }QPushButton:hover {background-color: rgb(57, 65, 80);border: 2px solid rgb(61, 70, 86);}\
                                                        QPushButton:pressed {background-color: rgb(35, 40, 49);border: 2px solid rgb(43, 50, 61);}")

    def sys_start(self):
        self.cams.start()
        self.glassCaptures.start()
        self.linelight.connect()
        self.plc.start()
        self.imgp.start()

        if self.Is_connected is False:
            self.Is_connected = True
            self.cams.connect_signals(self.glassCaptures,self.plc)
            self.glassCaptures.connect_signals(self.imgp,self.plc)
            self.imgp.connect_signals(self.plc,self.cams,self.linelight,self.menuTeach)
            self.plc.connect_signals(self.imgp,self.cams,self.linelight)


    def connectAll(self):

        if self.connectAll_btn_pressed is False:
            self.connectAll_btn_pressed = True
            self.ConnectAll_pushButton.setText("Stop All")
            self.ConnectAll_pushButton.setStyleSheet("QPushButton {\n	border: 2px solid rgb(52, 59, 72);\n	border-radius: 5px;	\n	background-color: rgb(85, 170, 255);\n}\nQPushButton:hover {\n	background-color: rgb(85, 170, 255);\n	border: 2px solid rgb(61, 70, 86);\n}\nQPushButton:pressed {	\n	background-color: rgb(35, 40, 49);\n	border: 2px solid rgb(43, 50, 61);\n}")
            self.staue_label.setText("連續檢測模式")

            self.start_continuous()
        else:
            self.connectAll_btn_pressed = False
            self.ConnectAll_pushButton.setText("Connect All")
            self.sys_stop()
            self.staue_label.setText("閒置模式")
            self.ConnectAll_pushButton.setStyleSheet("QPushButton {\n	border: 2px solid rgb(52, 59, 72);\n	border-radius: 5px;	\n	background-color: rgb(52, 59, 72);\n}\nQPushButton:hover {\n	background-color: rgb(57, 65, 80);\n	border: 2px solid rgb(61, 70, 86);\n}\nQPushButton:pressed {	\n	background-color: rgb(35, 40, 49);\n	border: 2px solid rgb(43, 50, 61);\n}")

    def start_continuous(self):

        self.sys_start()
        self.imgp.worker.continuous()

        self.actionPfsExport.setEnabled(False)
        self.actionPfsImport.setEnabled(False)
        self.LineLight_spinBox.setEnabled(False)
        self.LineLightOpen_pushButton.setEnabled(False)
        self.LineLightClose_pushButton.setEnabled(False)

    def start_single(self):

        self.sys_start()
        self.plc.stop()
        self.linelight.open()
        self.imgp.worker.single()
        self.staue_label.setText("單拍模式")
        self.OneShot_pushButton.setEnabled(False)
        self.OneShot_pushButton.setStyleSheet("QPushButton {border: 2px solid rgb(52, 59, 72);border-radius: 5px;background-color: gray; \
                                                        }QPushButton:hover {background-color: rgb(57, 65, 80);border: 2px solid rgb(61, 70, 86);} \
                                                        QPushButton:pressed {background-color: rgb(35, 40, 49);border: 2px solid rgb(43, 50, 61);}")



    def closeEvent(self, event):
        # if LAB_USED==1:
        #     print('LAB_USED')
        # else:
        #     print('ONLINE')
        #     # show_disk_info()
        #
        # if self.cam_left is not None:
        #     self.cam_left.Camera.Close()
        # if self.cam_right is not None:
        #     self.cam_right.Camera.Close()
        #
        os._exit(0)
        #
        # self.gc_left_worker.task_stop()
        # self.gc_left_thread.quit()
        # self.gc_left_thread.wait()
        #
        #
        # self.gc_right_worker.task_stop()
        # self.gc_right_thread.quit()
        # self.gc_right_thread.wait()
        #
        #
        # if self.linelight is not None:
        #     self.linelight.Close(value=0)
        #
        #
        # self.plc_worker.task_close()
        # self.plc_thread.quit()
        # self.plc_thread.wait()
        #
        # if self.imgp_thread.isFinished() is False:
        #     self.imgp_worker.close_pool()
        #     self.imgp_thread.quit()
        #     self.imgp_thread.wait()

        print("exit")


    def Button(self):
        # GET BT CLICKED
        btnWidget = self.sender()

        # PAGE CAMERA
        if btnWidget.objectName() == "btn_camera":
            self.stackedWidget.setCurrentWidget(self.page_camera)
            UIFunctions.resetStyle(self, "btn_camera")
            UIFunctions.labelPage(self, "Camera")
            btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet()))

        # PAGE SETTINGS
        if btnWidget.objectName() == "btn_settings":
            self.stackedWidget.setCurrentWidget(self.page_setting)
            UIFunctions.resetStyle(self, "btn_settings")
            UIFunctions.labelPage(self, "Setting")
            btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet()))

        # PAGE SETTINGS
        if btnWidget.objectName() == "btn_linelight":
            self.stackedWidget.setCurrentWidget(self.page_linelight)
            UIFunctions.resetStyle(self, "btn_linelight")
            UIFunctions.labelPage(self, "Line Light")
            btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet()))

        # PAGE btn_teach
        if btnWidget.objectName() == "btn_teach":
            self.menuTeach.update_Rcp_widget()
            self.stackedWidget.setCurrentWidget(self.page_teach)
            UIFunctions.resetStyle(self, "btn_teach")
            UIFunctions.labelPage(self, "Teach")
            btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet()))

    ## START ==> APP EVENTS

    ## EVENT ==> MOUSE DOUBLE CLICK
    ########################################################################
    def eventFilter(self, watched, event):
        if watched == self.le and event.type() == QtCore.QEvent.MouseButtonDblClick:
            print("pos: ", event.pos())
    ## ==> END ##

    ## EVENT ==> MOUSE CLICK
    ########################################################################
    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()
    ## ==> END ##

    ## EVENT ==> RESIZE EVENT
    ########################################################################
    def resizeEvent(self, event):
        # self.resizeFunction()
        return super(AOI_sys, self).resizeEvent(event)


# Raise error but continue!!
def exception_hook(exctype, value, Traceback):
    # Print the error and traceback
    print(exctype, value, Traceback)
    sys._excepthook(exctype, value, Traceback)

    # Call the normal Exception hook after
    # sys.exit(1)

    # Back up the reference to the exceptionhook
    sys._excepthook = sys.excepthook
    # Set the exception hook to our wrapping function
    sys.excepthook = exception_hook




if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeui.ttf')
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeuib.ttf')
    AOI_SYS = AOI_sys()
    sys.exit(app.exec_())


