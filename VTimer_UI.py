# coding: utf-8
"""
Created on Jul 28, 2019

@author: sanin
"""

import sys
import os
if os.path.realpath('../TangoUtils') not in sys.path: sys.path.append(os.path.realpath('../TangoUtils'))

from collections import deque

from tango import DevFailed

from TangoUtils import tango_exception_reason, tango_exception_description

from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
from PyQt5.QtCore import QTimer

from TangoWidgets.TangoAttribute import TangoAttribute
from TangoWidgets.TangoCheckBox import TangoCheckBox
from TangoWidgets.TangoLED import TangoLED
from TangoWidgets.TangoLabel import TangoLabel
from TangoWidgets.TangoAbstractSpinBox import TangoAbstractSpinBox
from TangoWidgets.RF_ready_LED import RF_ready_LED
from TangoWidgets.Lauda_ready_LED import Lauda_ready_LED

from config_logger import config_logger
from log_exception import log_exception
from TangoWidgets.Utils import *

APPLICATION_NAME = os.path.basename(__file__).replace('.py', '')
APPLICATION_NAME_SHORT = APPLICATION_NAME
APPLICATION_VERSION = '2.0'
CONFIG_FILE = APPLICATION_NAME_SHORT + '.json'
UI_FILE = APPLICATION_NAME_SHORT + '.ui'

TIMER_PERIOD = 300  # ms


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__(None)
        # logging config
        self.logger = config_logger()
        #
        self.saved_states = deque(maxlen=100)
        self.last_state = []
        # members definition
        self.n = 0
        self.elapsed = 0.0
        self.remained = 0.0
        self.loop_time = 0.0
        self.last_shot_time = 0.0
        # Load the Qt UI
        uic.loadUi(UI_FILE, self)
        # Default main window parameters
        self.resize(QSize(480, 640))  # size
        self.move(QPoint(50, 50))  # position
        self.setWindowTitle(APPLICATION_NAME)  # title
        # restore settings
        restore_settings(self, widgets=[self.spinBox], file_name=CONFIG_FILE)
        #
        self.timer_device_name = self.config.get('timer_device_name', 'binp/nbi/timer1')
        self.config['timer_device_name'] = self.timer_device_name
        self.period = self.config.get('period', 0.0)
        self.config['period'] = self.period
        # self.period = self.spinBox.value()
        self.spinBox.setValue(int(self.period))
        try:
            self.timer_device = tango.DeviceProxy(self.timer_device_name)
            self.timer_device.ping()
        except DevFailed as e:
            log_exception()
            txt = tango_exception_description(e)
            #     self.restore = True
            QMessageBox.critical(None, 'VTimer device is unreacheable',
                                 txt + '\nProgram will quit.', QMessageBox.Ok)
            exit(-111)
        # declare additional devices
        self.device_names = self.config.get('device_names', [])
        self.config['device_names'] = self.device_names
        self.devices = {}
        for d in self.device_names:
            try:
                self.devices[d] = tango.DeviceProxy(d)
                self.devices[d].ping()
            except DevFailed as e:
                txt = 'Can not connect device %s' % d
                log_exception(txt)
                # a = QMessageBox.question(None, f'VTimer critical error for {d}',
                #                          txt + '\n\nContinue?',
                #                          QMessageBox.Yes | QMessageBox.No)
                # if a == QMessageBox.No:
                #     exit(-111)
        # Widgets definition
        self.enable_widgets = [
            TangoCheckBox(self.timer_device_name + '/channel_enable0', self.checkBox_8),  # ch0           2
            TangoCheckBox(self.timer_device_name + '/channel_enable1', self.checkBox_9),  # ch1           3
            TangoCheckBox(self.timer_device_name + '/channel_enable2', self.checkBox_10),  # ch2          4
            TangoCheckBox(self.timer_device_name + '/channel_enable3', self.checkBox_11),  # ch3          5
            TangoCheckBox(self.timer_device_name + '/channel_enable4', self.checkBox_12),  # ch4
            TangoCheckBox(self.timer_device_name + '/channel_enable5', self.checkBox_13),  # ch5
            TangoCheckBox(self.timer_device_name + '/channel_enable6', self.checkBox_14),  # ch6
            TangoCheckBox(self.timer_device_name + '/channel_enable7', self.checkBox_15),  # ch7
            TangoCheckBox(self.timer_device_name + '/channel_enable8', self.checkBox_16),  # ch8
            TangoCheckBox(self.timer_device_name + '/channel_enable9', self.checkBox_17),  # ch9
            TangoCheckBox(self.timer_device_name + '/channel_enable10', self.checkBox_18),  # ch10
            TangoCheckBox(self.timer_device_name + '/channel_enable11', self.checkBox_19),  # ch11        13
        ]
        self.stop_widgets = [
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_stop0', self.spinBox_11),  # ch0        26
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_stop1', self.spinBox_13),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_stop2', self.spinBox_15),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_stop3', self.spinBox_17),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_stop4', self.spinBox_19),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_stop5', self.spinBox_21),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_stop6', self.spinBox_23),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_stop7', self.spinBox_25),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_stop8', self.spinBox_27),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_stop9', self.spinBox_29),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_stop10', self.spinBox_31),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_stop11', self.spinBox_33),  # ch11      37
        ]
        self.labels = [
            # timer labels from enabled channels
            TangoLabel(self.timer_device_name + '/channel_enable0', self.label_30, prop='label'),  # ch0
            TangoLabel(self.timer_device_name + '/channel_enable1', self.label_31, prop='label'),  # ch1
            TangoLabel(self.timer_device_name + '/channel_enable2', self.label_34, prop='label'),  # ch2
            TangoLabel(self.timer_device_name + '/channel_enable3', self.label_35, prop='label'),  # ch3
            TangoLabel(self.timer_device_name + '/channel_enable4', self.label_36, prop='label'),  # ch4
            TangoLabel(self.timer_device_name + '/channel_enable5', self.label_38, prop='label'),  # ch
            TangoLabel(self.timer_device_name + '/channel_enable6', self.label_39, prop='label'),  # ch
            TangoLabel(self.timer_device_name + '/channel_enable7', self.label_40, prop='label'),  # ch
            TangoLabel(self.timer_device_name + '/channel_enable8', self.label_41, prop='label'),  # ch
            TangoLabel(self.timer_device_name + '/channel_enable9', self.label_42, prop='label'),  # ch
            TangoLabel(self.timer_device_name + '/channel_enable10', self.label_43, prop='label'),  # ch
            TangoLabel(self.timer_device_name + '/channel_enable11', self.label_44, prop='label'),  # ch11
        ]
        self.start_widgets = [
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_start0', self.spinBox_10),  # ch1       14
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_start1', self.spinBox_12),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_start2', self.spinBox_14),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_start3', self.spinBox_16),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_start4', self.spinBox_18),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_start5', self.spinBox_20),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_start6', self.spinBox_22),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_start7', self.spinBox_24),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_start8', self.spinBox_26),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_start9', self.spinBox_28),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_start10', self.spinBox_30),  # ch
            TangoAbstractSpinBox(self.timer_device_name + '/pulse_start11', self.spinBox_32),  # ch11     25
        ]
        self.wtwdgts = [
            # TangoAbstractSpinBox(self.timer_device_name + '/Period', self.spinBox),  # period             0
            # TangoComboBox(self.timer_device_name + '/Start_mode', self.comboBox),  # single/periodical    1
            # TangoAbstractSpinBox('binp/nbi/adc0/Acq_start', self.spinBox_34),  # adc start
            # TangoAbstractSpinBox('binp/nbi/adc0/Acq_stop', self.spinBox_35),  # adc stop
        ]
        # timer on led
        self.timer_on_led = TangoLED(self.timer_device_name + '/pulse', self.pushButton_29)
        self.timer_on_led.attribute.force_read = True
        self.timer_on_led.attribute.sync_read = True
        #
        self.run_attribute = TangoAttribute(self.timer_device_name + '/run')
        # stop pulse at start-up
        self.stop_pulse()
        self.switch_to_single()
        # interlock widgets
        self.anode_power_led = TangoLED('binp/nbi/rfpowercontrol/anode_power_ok',
                                        self.pushButton_33)
        self.anode_power_led.attribute.sync_read = True
        # lauda
        self.lauda = Lauda_ready_LED('binp/nbi/laudapy/', self.pushButton_30)
        self.lauda.attribute.sync_read = True
        # RF system
        self.rf = RF_ready_LED('binp/nbi/timing/di60', self.pushButton_32)  # RF system ready
        self.rf.attribute.sync_read = True
        # PG offset
        self.pg = TangoLED('binp/nbi/pg_offset/output_state', self.pushButton_31, sync_read=True)

        # combine all processed widgets
        self.widgets = (self.labels + self.wtwdgts + self.enable_widgets + self.stop_widgets + self.start_widgets)

        # time of update for widgets
        self.wtime = [time.time() for w in self.widgets]

        # additional decorations

        # Connect signals with slots
        # single/periodical combo
        self.comboBox.currentIndexChanged.connect(self.single_periodical_callback)
        # run button
        self.pushButton.clicked.connect(self.run_button_clicked)
        # execute button
        self.pushButton_2.clicked.connect(self.execute_button_clicked)
        # period
        self.spinBox.valueChanged.connect(self.period_changed)

        # prevent non tango leds from changing color when clicked
        # self.pushButton_34.mouseReleaseEvent = self.absorb_event
        # self.pushButton_29.mouseReleaseEvent = self.absorb_event

        # resize main window
        self.resize_main_window()

        # populate comboBox_2 - scripts for timer
        self.populate_scripts()

        # lock timer for exclusive use of this app
        # self.lock_timer()

        self.mode = self.timer_device.mode
        if self.mode == 2:
            # hide some interface items
            self.comboBox.hide()
            self.spinBox.hide()
            self.label.hide()
            self.pushButton.hide()
            self.label_2.hide()
            self.label_3.hide()
            self.label_4.hide()
            self.label_5.hide()
            self.label_6.hide()
            self.label_7.hide()
            self.label_8.hide()
            self.label_9.hide()
            self.label_10.hide()
            self.label_46.hide()
            self.checkBox_20.hide()
            self.checkBox_21.hide()
            self.checkBox_22.hide()
            self.checkBox_23.hide()
            self.checkBox_20.setChecked(False)
            self.checkBox_21.setChecked(False)
            self.checkBox_22.setChecked(False)
            self.checkBox_23.setChecked(False)
            self.pushButton_30.hide()
            self.pushButton_31.hide()
            self.pushButton_32.hide()
            self.pushButton_33.hide()
            self.pushButton_34.hide()
            self.wtwdgts[-1].widget.hide()
            self.wtwdgts[-2].widget.hide()

        # Defile timer callback task and start timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timer_handler)
        self.timer.start(TIMER_PERIOD)
        # Welcome message
        print(APPLICATION_NAME + ' version ' + APPLICATION_VERSION + ' started')

    def lock_timer(self):
        if self.timer_device is not None:
            if self.timer_device.is_locked():
                self.logger.warning('Timer device is already locked')
                self.pushButton.setEnabled(False)
                self.comboBox.setEnabled(False)
            else:
                if self.timer_device.lock(100000):
                    self.logger.debug('Timer device locked successfully')
                else:
                    self.logger.error('Can not lock timer device')

    def populate_scripts(self):
        scripts = read_folder('scripts')
        truncated = [s.replace('.py', '') for s in scripts]
        for i in range(self.comboBox_2.count()):
            self.comboBox_2.removeItem(0)
        self.comboBox_2.insertItems(0, truncated)
        if 'SetDefault' in truncated:
            self.comboBox_2.setCurrentIndex(truncated.index('SetDefault'))

    def absorb_event(self, ev):
        pass

    def period_changed(self, v):
        self.period = v

    def check_protection_interlock(self):
        if self.checkBox_23.isChecked():
            self.pushButton_33.tango_widget.update()
            if not self.pushButton_33.isChecked():
                return False
        if self.checkBox_20.isChecked():
            self.pushButton_30.tango_widget.update()
            if not self.pushButton_30.isChecked():
                return False
        if self.checkBox_21.isChecked():
            self.pushButton_31.tango_widget.update()
            if not self.pushButton_31.isChecked():
                return False
        if self.checkBox_22.isChecked():
            self.pushButton_32.tango_widget.update()
            if not self.pushButton_32.isChecked():
                return False
        return True

    def execute_button_clicked(self):
        file_name = ''
        try:
            file_name = os.path.join('scripts', self.comboBox_2.currentText() + '.py')
            with open(file_name, 'r') as scriptfile:
                s = scriptfile.read()
                exec(s)
                self.logger.debug('Script %s executed', file_name)
                self.comboBox_2.setStyleSheet('')
        except KeyboardInterrupt:
            raise
        except:
            self.comboBox_2.setStyleSheet('color: red')
            log_exception('Error script %s execution', file_name)

    def resize_main_window(self):
        self.frame.setVisible(True)
        self.resize(QSize(self.gridLayout_2.sizeHint().width(),
                          self.gridLayout_2.sizeHint().height() +
                          self.gridLayout_3.sizeHint().height()))

    def switch_to_single(self):
        self.label_4.setVisible(False)
        self.label_5.setVisible(False)
        # run button
        self.pushButton.setText('Shoot')
        # stop pulse
        self.stop_pulse()
        self.periodical = 0
        self.comboBox.blockSignals(True)
        self.comboBox.setCurrentIndex(0)
        self.comboBox.blockSignals(False)

    def switch_to_periodical(self):
        self.label_4.setVisible(True)
        self.label_5.setVisible(True)
        # run button
        self.pushButton.setText('Stop')
        self.periodical = 1
        self.comboBox.blockSignals(True)
        self.comboBox.setCurrentIndex(1)
        self.comboBox.blockSignals(False)
        self.start_pulse()

    def single_periodical_callback(self, value):
        if value == 0:  # switch to single
            self.switch_to_single()
        elif value == 1:  # switch to periodical
            # check protection interlock
            if not self.check_protection_interlock():
                self.logger.error('Protection - Mode switch has been rejected')
                self.switch_to_single()
                # self.comboBox.setStyleSheet('border: 3px solid red')
                QMessageBox.critical(self, 'Protection',
                                     'Protection interlock.\nMode switch has been rejected.',
                                     QMessageBox.Ok)
                return
            if self.is_pulse_on():
                # self.comboBox.setStyleSheet('border: 3px solid red')
                self.logger.error('Shot is on - Mode switch has been rejected')
                QMessageBox.critical(self, 'Shot in on',
                                     'Shot is on.\nMode switch has been rejected.',
                                     QMessageBox.Ok)
                return
            self.switch_to_periodical()

    def read_max_time(self):
        mt = 0.0
        for i, w in enumerate(self.enable_widgets):
            w.attribute.read()
            if w.attribute.value():
                mt = max(mt, self.stop_widgets[i].get_widget_value())
        return mt

    def update_ready_led(self):
        if self.check_protection_interlock():
            self.pushButton_34.setChecked(True)
        else:
            self.pushButton_34.setChecked(False)
            if self.is_pulse_on():
                self.pulse_off('Protection interlock')

    def run_button_clicked(self, value):
        if self.mode == 2:  # slave
            if self.is_pulse_on():  # pulse is on
                self.pulse_off('Interrupted by user.')
                return
        if self.comboBox.currentIndex() == 0:  # single
            if self.is_pulse_on():  # pulse is on
                self.pulse_off('Interrupted by user.')
            else:
                # check protection interlock
                if not self.check_protection_interlock():
                    self.logger.error('Shot has been rejected')
                    # self.pushButton.setStyleSheet('border: 3px solid red')
                    QMessageBox.critical(self, 'Interlock',
                                         'Shot has been rejected', QMessageBox.Ok)
                    return
                self.start_pulse()
        elif self.comboBox.currentIndex() == 1:  # periodical
            if self.is_pulse_on():  # pulse is on
                self.pulse_off('Interrupted by user!')
            self.comboBox.setCurrentIndex(0)

    def pulse_off(self, msg='Interrupted by user.'):
        # self.save_state()
        n = 0
        try:
            self.stop_pulse()
        except KeyboardInterrupt:
            raise
        except:
            n += 1
        if n <= 0:
            # a = QMessageBox.question(self, 'Shot Interrupted',
            #                          msg + '\n\nRestore enabled channels?',
            #                          QMessageBox.Yes | QMessageBox.No)
            # if a == QMessageBox.Yes:
            #     self.restore = True
            # # self.max_time = 0.0
            self.timer_on_led.update(False)
            return
        QMessageBox.critical(self, 'Can not stop pulse!',
                             'Can not stop pulse!', QMessageBox.Ok)
        self.logger.error("Can not stop pulse")
        self.logger.debug("Last Exception ", exc_info=True)
        # self.restore = False

    def save_state(self, state=None):
        if state is None:
            state = self.get_state()
        if state == self.last_state:
            self.logger.debug('State save ignored')
            return None
        self.saved_states.append(state)
        self.last_state = state
        self.logger.debug('State saved to index %s', len(self.saved_states) - 1)
        return state

    def get_state(self):
        func_list = [self.checkBox_8.isChecked,
                     self.spinBox_10.value,
                     self.spinBox_11.value,
                     self.checkBox_9.isChecked,
                     self.spinBox_12.value,
                     self.spinBox_13.value,
                     self.checkBox_10.isChecked,
                     self.spinBox_14.value,
                     self.spinBox_15.value,
                     self.checkBox_11.isChecked,
                     self.spinBox_16.value,
                     self.spinBox_17.value,
                     self.checkBox_12.isChecked,
                     self.spinBox_18.value,
                     self.spinBox_19.value,
                     self.checkBox_13.isChecked,
                     self.spinBox_20.value,
                     self.spinBox_21.value,
                     self.checkBox_14.isChecked,
                     self.spinBox_22.value,
                     self.spinBox_23.value,
                     self.checkBox_15.isChecked,
                     self.spinBox_24.value,
                     self.spinBox_25.value,
                     self.checkBox_16.isChecked,
                     self.spinBox_26.value,
                     self.spinBox_27.value,
                     self.checkBox_17.isChecked,
                     self.spinBox_28.value,
                     self.spinBox_29.value,
                     self.checkBox_18.isChecked,
                     self.spinBox_30.value,
                     self.spinBox_31.value,
                     self.checkBox_19.isChecked,
                     self.spinBox_32.value,
                     self.spinBox_33.value,
                     self.spinBox_34.value,
                     self.spinBox_35.value]
        state = [f() for f in func_list]
        return state

    def set_state(self, state=None):
        if state is None:
            if len(self.saved_states) <= 0:
                self.logger.info('State stack is empty')
                return
            state = self.saved_states.pop()
            state_id = 'index %s' % len(self.saved_states)
        else:
            state_id = str(state)[:10]
        func_list = [self.checkBox_8.setChecked,
                     self.spinBox_10.setValue,
                     self.spinBox_11.setValue,
                     self.checkBox_9.setChecked,
                     self.spinBox_12.setValue,
                     self.spinBox_13.setValue,
                     self.checkBox_10.setChecked,
                     self.spinBox_14.setValue,
                     self.spinBox_15.setValue,
                     self.checkBox_11.setChecked,
                     self.spinBox_16.setValue,
                     self.spinBox_17.setValue,
                     self.checkBox_12.setChecked,
                     self.spinBox_18.setValue,
                     self.spinBox_19.setValue,
                     self.checkBox_13.setChecked,
                     self.spinBox_20.setValue,
                     self.spinBox_21.setValue,
                     self.checkBox_14.setChecked,
                     self.spinBox_22.setValue,
                     self.spinBox_23.setValue,
                     self.checkBox_15.setChecked,
                     self.spinBox_24.setValue,
                     self.spinBox_25.setValue,
                     self.checkBox_16.setChecked,
                     self.spinBox_26.setValue,
                     self.spinBox_27.setValue,
                     self.checkBox_17.setChecked,
                     self.spinBox_28.setValue,
                     self.spinBox_29.setValue,
                     self.checkBox_18.setChecked,
                     self.spinBox_30.setValue,
                     self.spinBox_31.setValue,
                     self.checkBox_19.setChecked,
                     self.spinBox_32.setValue,
                     self.spinBox_33.setValue,
                     self.spinBox_34.setValue,
                     self.spinBox_35.setValue]
        for i in range(len(state)):
            func_list[i](state[i])
        self.last_state = state
        self.logger.debug('State has been restored from %s', state_id)
        return state

    def onQuit(self):
        # Save global settings
        self.timer.stop()
        self.switch_to_single()
        save_settings(self, widgets=[self.spinBox], file_name=CONFIG_FILE)

    def is_pulse_on(self):
        return self.timer_on_led.get_widget_value()

    def update_timer_on_led(self):
        self.timer_on_led.update(decorate_only=False)

    def update_remained(self):
        self.remained = max(0, self.last_shot_time + self.period - time.time())
        if self.remained < 0:
            txt = ''
        else:
            txt = '%d s' % self.remained
        self.label_5.setText(txt)

    def update_elapsed(self):
        self.elapsed = time.time() - self.last_shot_time
        if self.elapsed > 60*60*24:
            txt = 'long time'
        else:
            txt = '%d s' % self.elapsed
        self.label_3.setText(txt)

    def start_pulse(self):
        self.timer_device.command_inout('start_pulse')
        self.last_shot_time = time.time()

    def stop_pulse(self):
        self.run_attribute.write(0)

    def timer_handler(self):
        # self.logger.debug("*** entry")
        t0 = time.time()
        try:
            self.update_timer_on_led()
            if self.mode != 2:
                self.update_ready_led()
                # periodical shooting
                if self.periodical and self.period > 0.0:
                    if time.time() - self.last_shot_time >= self.period:
                        if self.is_pulse_on():
                            QMessageBox.critical(self, 'Wrong Period',
                                                 'Shot is on during period expired', QMessageBox.Ok)
                            self.single_periodical_callback(0)
                        else:
                            self.start_pulse()
                self.update_elapsed()
                self.update_remained()
            if self.is_pulse_on():
                # pulse is ON LED -> ON
                if self.mode == 2:
                    self.pushButton.show()
                self.pushButton.setStyleSheet('color: red; font: bold')
                self.pushButton.setText('Stop')
                # check for external trigger
                if self.last_shot_time + (self.read_max_time() / 1000.) < time.time():
                    self.last_shot_time = time.time()
                    self.logger.info('External trigger detected')
            else:
                # pulse is OFF LED -> OFF
                if self.mode == 2:
                    self.pushButton.hide()
                self.pushButton.setStyleSheet('')
                if self.comboBox.currentIndex() == 0:
                    self.pushButton.setText('Shoot')
            #
            # main loop updating widgets
            count = 0
            while time.time() - t0 < TIMER_PERIOD / 1000.00 * 0.7:
                if self.n < len(self.widgets) and self.widgets[self.n].widget.isVisible():
                    self.widgets[self.n].update()
                    if self.mode == 2:
                        if not self.widgets[self.n].compare():
                            self.widgets[self.n].widget.setStyleSheet('color: blue')
                            if time.time() - self.wtime[self.n] > 2.0:
                                self.widgets[self.n].set_widget_value()
                        else:
                            self.wtime[self.n] = time.time()
                self.n += 1
                if self.n >= len(self.widgets):
                    self.n = 0
                count += 1
                if count == len(self.widgets):
                    break
            self.loop_time = time.time() - t0
        except KeyboardInterrupt:
            raise
        except:
            log_exception('Unexpected exception in timer callback')
        # self.logger.debug("total time %s s", time.time() - t0)


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        CONFIG_FILE = sys.argv[1]
        if not CONFIG_FILE.endswith('.json'):
            CONFIG_FILE += '.json'
    # Create the GUI application
    app = QApplication(sys.argv)
    # Instantiate the main window
    # # splash = QtWidgets.QSplashScreen(QtGui.QPixmap("IAM.jpg") )
    # # splash.showMessage("Connecting to TANGO devices ...",
    # #              QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom, QtCore.Qt.white)
    # # splash.show()                  # Отображаем заставку
    # QtWidgets.qApp.processEvents() # Запускаем оборот цикла
    window = MainWindow()
    app.aboutToQuit.connect(window.onQuit)
    title = f"Vtimer UI v.{APPLICATION_VERSION}"
    title = window.config.get("main_window", {"title": title})["title"]
    window.setWindowTitle(title)
    icon = window.config.get("icon_file", 'timer_icon2.png')
    window.setWindowIcon(QtGui.QIcon(icon))  # icon
    # window.setWindowIcon(QtGui.QIcon('timer.ico'))  # icon
    window.show()
    # splash.finish(window)	# Скрываем заставку
    sys.exit(app.exec_())
