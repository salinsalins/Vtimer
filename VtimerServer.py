#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Vtimer tango device server
import json
import os
import sys
import time

from h5py.h5t import cfg

_u = os.path.dirname(os.path.realpath(sys.argv[0]))
_util_path = os.path.join(os.path.split(_u)[0], 'TangoUtils')
if _util_path not in sys.path: sys.path.append(_util_path)
del _u, _util_path

from tango import AttrQuality, AttrWriteType, DispLevel
from tango import DevState
from tango.server import attribute, command

from TangoServerPrototype import TangoServerPrototype
from Vtimer import Vtimer

APPLICATION_NAME = 'Vtimer Python Tango Server'
APPLICATION_NAME_SHORT = os.path.basename(__file__).replace('.py', '')
APPLICATION_VERSION = '1.5'

DEFAULT_PORT = 'COM17'
DEFAULT_ADDRESS = 1
DEFAULT_READ_TIMEOUT = 1.0
DEFAULT_CONFIG = {'port': 0, 'COM17': True, 'address': 1, 'device_type': 'Vtimer v1.0',
                  'mode': 0, 'last_duration': 0, 'last_time': 0.0,
                  'output': True, 'duration': 0, 'period': 0,
                  'periodic_start': False, 'auto_rearm': True, 'restore_state': True,
                  'channel_enable0': False, 'pulse_start0': 0, 'pulse_stop0': 1,
                  'channel_enable1': False, 'pulse_start1': 0, 'pulse_stop1': 1,
                  'channel_enable2': False, 'pulse_start2': 0, 'pulse_stop2': 1,
                  'channel_enable3': False, 'pulse_start3': 0, 'pulse_stop3': 1,
                  'channel_enable4': False, 'pulse_start4': 0, 'pulse_stop4': 1,
                  'channel_enable5': False, 'pulse_start5': 0, 'pulse_stop5': 1,
                  'channel_enable6': False, 'pulse_start6': 0, 'pulse_stop6': 1,
                  'channel_enable7': False, 'pulse_start7': 0, 'pulse_stop7': 1,
                  'channel_enable8': False, 'pulse_start8': 0, 'pulse_stop8': 1,
                  'channel_enable9': False, 'pulse_start9': 0, 'pulse_stop9': 1,
                  'channel_enable10': False, 'pulse_start10': 0, 'pulse_stop10': 1,
                  'channel_enable11': False, 'pulse_start11': 0, 'pulse_stop11': 1
                  }


class VtimerServer(TangoServerPrototype):
    server_version_value = APPLICATION_VERSION
    server_name_value = APPLICATION_NAME

    # region ---------------- standard attributes --------------
    port = attribute(label="Port", dtype=str,
                     display_level=DispLevel.OPERATOR,
                     access=AttrWriteType.READ,
                     unit="", format="%s",
                     doc="COM port (Default COM17)")

    address = attribute(label="Address", dtype=int,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="", format="%d",
                        doc="Address (Default 1)")

    device_type = attribute(label="Vtimer Type", dtype=str,
                            display_level=DispLevel.OPERATOR,
                            access=AttrWriteType.READ,
                            unit="", format="%s",
                            doc="Vtimer device type")

    # endregion

    # region ---------------- custom attributes --------------
    run = attribute(label="Run", dtype=int,
                    display_level=DispLevel.OPERATOR,
                    access=AttrWriteType.READ_WRITE,
                    min_value=0,
                    max_value=3,
                    unit="",
                    doc="Run register")

    mode = attribute(label="Mode", dtype=int,
                     display_level=DispLevel.OPERATOR,
                     access=AttrWriteType.READ_WRITE,
                     min_value=0,
                     max_value=2,
                     unit="",
                     doc="Mode register")

    last_duration = attribute(label="Last Run", dtype=int,
                              display_level=DispLevel.OPERATOR,
                              access=AttrWriteType.READ,
                              unit="ms",
                              format="%d",
                              doc="Last script duration [ms]")

    last_time = attribute(label="Last Shot Time", dtype=float,
                          display_level=DispLevel.OPERATOR,
                          access=AttrWriteType.READ,
                          unit="",
                          format="%f",
                          doc="Last shot time UTF")

    duration = attribute(label="Script duration", dtype=int,
                         display_level=DispLevel.OPERATOR,
                         access=AttrWriteType.READ_WRITE,
                         unit="ms", format="%d",
                         doc="Total script duration [ms]")

    output = attribute(label="Output", dtype=bool,
                       display_level=DispLevel.OPERATOR,
                       access=AttrWriteType.READ_WRITE,
                       unit="",
                       doc="Optical output control")

    pulse = attribute(label="Pulse state", dtype=bool,
                      display_level=DispLevel.OPERATOR,
                      access=AttrWriteType.READ,
                      unit="",
                      doc="Pulse ON/OFF state")

    faults = attribute(label="Faults register", dtype=int,
                       display_level=DispLevel.OPERATOR,
                       access=AttrWriteType.READ,
                       unit="",
                       doc="Faults register state")

    period = attribute(label="Period", dtype=float,
                       display_level=DispLevel.OPERATOR,
                       access=AttrWriteType.READ_WRITE,
                       unit="s",
                       doc="Automatic start period [s]")

    periodic_start = attribute(label="Auto start mode", dtype=bool,
                           display_level=DispLevel.OPERATOR,
                           access=AttrWriteType.READ_WRITE,
                           unit="",
                           doc="Auto start mode")

    auto_rearm = attribute(label="Auto rearm after pulse", dtype=bool,
                           display_level=DispLevel.OPERATOR,
                           access=AttrWriteType.READ_WRITE,
                           unit="",
                           doc="Auto rearm mode")

    restore_state = attribute(label="Restore state", dtype=bool,
                           display_level=DispLevel.OPERATOR,
                           access=AttrWriteType.READ_WRITE,
                           unit="",
                           doc="Restore state after restart")
    # endregion

    # region ---------------- channels --------------
    channel_enable0 = attribute(label="Channel 0", dtype=bool,
                                display_level=DispLevel.OPERATOR,
                                access=AttrWriteType.READ_WRITE,
                                unit="",
                                doc="Channel 0 ON/OFF state")

    pulse_start0 = attribute(label="Channel 0 start", dtype=int,
                             display_level=DispLevel.OPERATOR,
                             access=AttrWriteType.READ_WRITE,
                             unit="ms",
                             doc="Channel 0 start time [ms]")

    pulse_stop0 = attribute(label="Channel 0 stop", dtype=int,
                            display_level=DispLevel.OPERATOR,
                            access=AttrWriteType.READ_WRITE,
                            unit="ms",
                            doc="Channel 1 stop time [ms]")

    channel_enable1 = attribute(label="Channel 1", dtype=bool,
                                display_level=DispLevel.OPERATOR,
                                access=AttrWriteType.READ_WRITE,
                                unit="",
                                doc="Channel 1 ON/OFF state")

    pulse_start1 = attribute(label="Channel 1 start", dtype=int,
                             display_level=DispLevel.OPERATOR,
                             access=AttrWriteType.READ_WRITE,
                             unit="ms",
                             doc="Channel 1 start time [ms]")

    pulse_stop1 = attribute(label="Channel 1 stop", dtype=int,
                            display_level=DispLevel.OPERATOR,
                            access=AttrWriteType.READ_WRITE,
                            unit="ms",
                            doc="Channel 1 stop time [ms]")

    channel_enable2 = attribute(label="Channel 2", dtype=bool,
                                display_level=DispLevel.OPERATOR,
                                access=AttrWriteType.READ_WRITE,
                                unit="",
                                doc="Channel 2 ON/OFF state")

    pulse_start2 = attribute(label="Channel 2 start", dtype=int,
                             display_level=DispLevel.OPERATOR,
                             access=AttrWriteType.READ_WRITE,
                             unit="ms",
                             doc="Channel 2 start time [ms]")

    pulse_stop2 = attribute(label="Channel 2 stop", dtype=int,
                            display_level=DispLevel.OPERATOR,
                            access=AttrWriteType.READ_WRITE,
                            unit="ms",
                            doc="Channel 2 stop time [ms]")

    channel_enable3 = attribute(label="Channel 3", dtype=bool,
                                display_level=DispLevel.OPERATOR,
                                access=AttrWriteType.READ_WRITE,
                                unit="",
                                doc="Channel 3 ON/OFF state")

    pulse_start3 = attribute(label="Channel 3 start", dtype=int,
                             display_level=DispLevel.OPERATOR,
                             access=AttrWriteType.READ_WRITE,
                             unit="ms",
                             doc="Channel 3 start time [ms]")

    pulse_stop3 = attribute(label="Channel 3 stop", dtype=int,
                            display_level=DispLevel.OPERATOR,
                            access=AttrWriteType.READ_WRITE,
                            unit="ms",
                            doc="Channel 3 stop time [ms]")

    channel_enable4 = attribute(label="Channel 4", dtype=bool,
                                display_level=DispLevel.OPERATOR,
                                access=AttrWriteType.READ_WRITE,
                                unit="",
                                doc="Channel 4 ON/OFF state")

    pulse_start4 = attribute(label="Channel 4 start", dtype=int,
                             display_level=DispLevel.OPERATOR,
                             access=AttrWriteType.READ_WRITE,
                             unit="ms",
                             doc="Channel 4 start time [ms]")

    pulse_stop4 = attribute(label="Channel 4 stop", dtype=int,
                            display_level=DispLevel.OPERATOR,
                            access=AttrWriteType.READ_WRITE,
                            unit="ms",
                            doc="Channel 4 stop time [ms]")

    channel_enable5 = attribute(label="Channel 5", dtype=bool,
                                display_level=DispLevel.OPERATOR,
                                access=AttrWriteType.READ_WRITE,
                                unit="",
                                doc="Channel 5 ON/OFF state")

    pulse_start5 = attribute(label="Channel 5 start", dtype=int,
                             display_level=DispLevel.OPERATOR,
                             access=AttrWriteType.READ_WRITE,
                             unit="ms",
                             doc="Channel 5 start time [ms]")

    pulse_stop5 = attribute(label="Channel 5 stop", dtype=int,
                            display_level=DispLevel.OPERATOR,
                            access=AttrWriteType.READ_WRITE,
                            unit="ms",
                            doc="Channel 5 stop time [ms]")

    channel_enable6 = attribute(label="Channel 6", dtype=bool,
                                display_level=DispLevel.OPERATOR,
                                access=AttrWriteType.READ_WRITE,
                                unit="",
                                doc="Channel 6 ON/OFF state")

    pulse_start6 = attribute(label="Channel 6 start", dtype=int,
                             display_level=DispLevel.OPERATOR,
                             access=AttrWriteType.READ_WRITE,
                             unit="ms",
                             doc="Channel 6 start time [ms]")

    pulse_stop6 = attribute(label="Channel 6 stop", dtype=int,
                            display_level=DispLevel.OPERATOR,
                            access=AttrWriteType.READ_WRITE,
                            unit="ms",
                            doc="Channel 6 stop time [ms]")

    channel_enable7 = attribute(label="Channel 7", dtype=bool,
                                display_level=DispLevel.OPERATOR,
                                access=AttrWriteType.READ_WRITE,
                                unit="",
                                doc="Channel 7 ON/OFF state")

    pulse_start7 = attribute(label="Channel 7 start", dtype=int,
                             display_level=DispLevel.OPERATOR,
                             access=AttrWriteType.READ_WRITE,
                             unit="ms",
                             doc="Channel 7 start time [ms]")

    pulse_stop7 = attribute(label="Channel 7 stop", dtype=int,
                            display_level=DispLevel.OPERATOR,
                            access=AttrWriteType.READ_WRITE,
                            unit="ms",
                            doc="Channel 7 stop time [ms]")

    channel_enable8 = attribute(label="Channel 8", dtype=bool,
                                display_level=DispLevel.OPERATOR,
                                access=AttrWriteType.READ_WRITE,
                                unit="",
                                doc="Channel 8 ON/OFF state")

    pulse_start8 = attribute(label="Channel 8 start", dtype=int,
                             display_level=DispLevel.OPERATOR,
                             access=AttrWriteType.READ_WRITE,
                             unit="ms",
                             doc="Channel 8 start time [ms]")

    pulse_stop8 = attribute(label="Channel 8 stop", dtype=int,
                            display_level=DispLevel.OPERATOR,
                            access=AttrWriteType.READ_WRITE,
                            unit="ms",
                            doc="Channel 8 stop time [ms]")

    channel_enable9 = attribute(label="Channel 9", dtype=bool,
                                display_level=DispLevel.OPERATOR,
                                access=AttrWriteType.READ_WRITE,
                                unit="",
                                doc="Channel 9 ON/OFF state")

    pulse_start9 = attribute(label="Channel 9 start", dtype=int,
                             display_level=DispLevel.OPERATOR,
                             access=AttrWriteType.READ_WRITE,
                             unit="ms",
                             doc="Channel 9 start time [ms]")

    pulse_stop9 = attribute(label="Channel 9 stop", dtype=int,
                            display_level=DispLevel.OPERATOR,
                            access=AttrWriteType.READ_WRITE,
                            unit="ms",
                            doc="Channel 9 stop time [ms]")

    channel_enable10 = attribute(label="Channel 10", dtype=bool,
                                 display_level=DispLevel.OPERATOR,
                                 access=AttrWriteType.READ_WRITE,
                                 unit="",
                                 doc="Channel 10 ON/OFF state")

    pulse_start10 = attribute(label="Channel 10 start", dtype=int,
                              display_level=DispLevel.OPERATOR,
                              access=AttrWriteType.READ_WRITE,
                              unit="ms",
                              doc="Channel 10 start time [ms]")

    pulse_stop10 = attribute(label="Channel 10 stop", dtype=int,
                             display_level=DispLevel.OPERATOR,
                             access=AttrWriteType.READ_WRITE,
                             unit="ms",
                             doc="Channel 10 stop time [ms]")

    channel_enable11 = attribute(label="Channel 11", dtype=bool,
                                 display_level=DispLevel.OPERATOR,
                                 access=AttrWriteType.READ_WRITE,
                                 unit="",
                                 doc="Channel 11 ON/OFF state")

    pulse_start11 = attribute(label="Channel 11 start", dtype=int,
                              display_level=DispLevel.OPERATOR,
                              access=AttrWriteType.READ_WRITE,
                              unit="ms",
                              doc="Channel 5 start time [ms]")

    pulse_stop11 = attribute(label="Channel 11 stop", dtype=int,
                             display_level=DispLevel.OPERATOR,
                             access=AttrWriteType.READ_WRITE,
                             unit="ms",
                             doc="Channel 11 stop time [ms]")

    # endregion

    def init_device(self):
        super().init_device()
        #
        self.pre = f'{self.get_name()} Vtimer'
        msg = f'Initialization'
        self.set_state(DevState.INIT, msg)
        self.debug(msg)
        # set default config
        if not hasattr(self, 'config'):
            self.config = {}
        for opt in DEFAULT_CONFIG:
            if opt not in self.config:
                self.config[opt] = DEFAULT_CONFIG[opt]
        if self.config.get('restore_state', False):
            DEFAULT_CONFIG.update(self.config)
            self.config.update(DEFAULT_CONFIG)
        # default values
        self.ready = False
        self.period_value = self.config['period']
        self.periodic_start_value = self.config['periodic_start']
        self.last_time_value = self.config['last_time']
        self.auto_rearm_value = self.config['auto_rearm']
        self.restore_state_value = self.config['restore_state']
        #
        kwargs = {}
        # port and address from config
        port = self.config.get('port', DEFAULT_PORT)
        addr = self.config.get('addr', DEFAULT_ADDRESS)
        kwargs['logger'] = self.logger
        kwargs['read_timeout'] = self.config.get('read_timeout', DEFAULT_READ_TIMEOUT)
        # create Vtimer device
        self.tmr = Vtimer(port, addr, **kwargs)
        self.pre = f'{self.get_name()} {self.tmr.pre}'
        # if device OK, initialize attribute defaults
        if self.tmr.ready:
            self.write_mode(self.config['mode'])
            self.write_output(self.config['output'])
            self.write_duration(self.config['duration'])
            for n in range(0, 12):
                aname = f'channel_enable{n}'
                setattr(self, aname, self.config[aname])
                aname = f'channel_start{n}'
                setattr(self, aname, self.config[aname])
                aname = f'channel_stop{n}'
                setattr(self, aname, self.config[aname])
            self.run.set_write_value(self.run)
            self.mode.set_write_value(self.mode)
            self.output.set_write_value(self.output)
            self.period.set_write_value(self.period)
            self.duration.set_write_value(self.duration)
            self.periodic_start.set_write_value(self.periodic_start)
            self.auto_rearm.set_write_value(self.auto_rearm)
            self.restore_state.set_write_value(self.restore_state)
            # set state to running
            msg = 'Created successfully'
            self.set_state(DevState.RUNNING, msg)
            self.info(msg)
        else:
            msg = 'Created with errors'
            self.set_state(DevState.FAULT, msg)
            self.error(msg)
        self.save_state()

    def delete_device(self):
        self.save_state()
        self.tmr.__del__()
        super().delete_device()
        msg = 'Device has been deleted'
        self.info(msg)

    # region ---------------- attributes read --------------
    def read_port(self):
        if self.tmr.ready:
            self.set_running()
        else:
            self.set_fault()
        return self.tmr.port

    def read_address(self):
        if self.tmr.ready:
            self.set_running()
        else:
            self.set_fault()
        return self.tmr.addr

    def read_device_type(self):
        if self.tmr.ready:
            self.set_running()
            return self.tmr.id
        else:
            self.set_fault()
            return "Not Ready or Uninitialized"

    def read_auto_rearm(self):
        if self.tmr.ready:
            self.set_running()
        else:
            self.set_fault()
        return self.auto_rearm_value

    def read_restore_state(self):
        if self.tmr.ready:
            self.set_running()
        else:
            self.set_fault()
        return self.restore_state_value

    # endregion

    # region ---------------- custom attributes read --------------
    def read_periodic_start(self):
        if self.tmr.ready:
            self.set_running()
        else:
            self.set_fault()
        return self.periodic_start_value

    def read_period(self):
        if self.tmr.ready:
            self.set_running()
        else:
            self.set_fault()
        return self.period_value

    def read_run(self):
        value = self.tmr.read_run()
        if value >= 0:
            self.run.set_quality(AttrQuality.ATTR_VALID)
            self.set_running()
            return value
        self.run.set_quality(AttrQuality.ATTR_INVALID)
        msg = 'Run State Read Error'
        self.set_fault(msg)
        return 0

    def read_mode(self):
        value = self.tmr.read_mode()
        if value >= 0:
            self.mode.set_quality(AttrQuality.ATTR_VALID)
            self.set_running()
            return value
        self.mode.set_quality(AttrQuality.ATTR_INVALID)
        msg = 'Mode Read Error'
        self.set_fault(msg)
        return 0

    def read_duration(self):
        value = self.tmr.read_duration()
        if value >= 0:
            self.duration.set_quality(AttrQuality.ATTR_VALID)
            self.duration.set_write_value(value)
            self.set_running()
            return value
        self.duration.set_quality(AttrQuality.ATTR_INVALID)
        msg = 'Duration Read Error'
        self.set_fault(msg)
        return 0

    def read_last_duration(self):
        value = self.tmr.read_last()
        if value >= 0:
            self.last_duration.set_quality(AttrQuality.ATTR_VALID)
            self.set_running()
            return value
        self.last_duration.set_quality(AttrQuality.ATTR_INVALID)
        msg = 'Run Time Read Error'
        self.set_fault(msg)
        return 0

    def read_last_time(self):
        if self.tmr.ready:
            self.set_running()
        else:
            self.set_fault()
        return self.last_time_value

    def read_output(self):
        value = self.tmr.read_output()
        if value >= 0:
            self.output.set_quality(AttrQuality.ATTR_VALID)
            self.set_running()
            return bool(value)
        self.output.set_quality(AttrQuality.ATTR_INVALID)
        msg = 'Output State Read Error'
        self.set_fault(msg)
        return False

    def read_pulse(self):
        value = self.tmr.read_status()
        if value >= 0:
            self.pulse.set_quality(AttrQuality.ATTR_VALID)
            self.set_running()
            return bool(value)
        self.pulse.set_quality(AttrQuality.ATTR_INVALID)
        msg = 'Pulse ON|OFF State Read Error'
        self.set_fault(msg)
        return False

    def read_faults(self):
        value = self.tmr.read_fault()
        if value >= 0:
            self.faults.set_quality(AttrQuality.ATTR_VALID)
            self.set_running()
            return value
        self.faults.set_quality(AttrQuality.ATTR_INVALID)
        msg = 'Faults Register Read Error'
        self.set_fault(msg)
        return False

    def read_channel_n(self, n):
        name = f'channel_enable{n}'
        value = self.tmr.read_channel_enable(n + 1)
        if value >= 0:
            getattr(self, name).set_quality(AttrQuality.ATTR_VALID)
            self.set_running()
            return bool(value)
        getattr(self, name).set_quality(AttrQuality.ATTR_INVALID)
        msg = f'Channel {n} State Read Error'
        self.set_fault(msg)
        return False

    def read_pulse_start_n(self, n):
        name = f'pulse_start{n}'
        value = self.tmr.read_channel_start(n + 1)
        if value >= 0:
            getattr(self, name).set_quality(AttrQuality.ATTR_VALID)
            return value
        getattr(self, name).set_quality(AttrQuality.ATTR_INVALID)
        msg = f'Channel {n} Start Time Read Error'
        self.set_fault(msg)
        return False

    def read_pulse_stop_n(self, n):
        name = f'pulse_stop{n}'
        value = self.tmr.read_channel_stop(n + 1)
        if value >= 0:
            getattr(self, name).set_quality(AttrQuality.ATTR_VALID)
            # self.logger.debug('read %d %s', n, value)
            return value
        getattr(self, name).set_quality(AttrQuality.ATTR_INVALID)
        msg = f'Channel {n} Stop Time Read Error'
        self.set_fault(msg)
        return False
    # endregion

    # region ---------------- channel state attributes read --------------
    def read_channel_enable0(self):
        return self.read_channel_n(0)

    def read_pulse_start0(self):
        return self.read_pulse_start_n(0)

    def read_pulse_stop0(self):
        return self.read_pulse_stop_n(0)

    def read_channel_enable1(self):
        return self.read_channel_n(1)

    def read_pulse_start1(self):
        return self.read_pulse_start_n(1)

    def read_pulse_stop1(self):
        return self.read_pulse_stop_n(1)

    def read_channel_enable2(self):
        return self.read_channel_n(2)

    def read_pulse_start2(self):
        return self.read_pulse_start_n(2)

    def read_pulse_stop2(self):
        return self.read_pulse_stop_n(2)

    def read_channel_enable3(self):
        return self.read_channel_n(3)

    def read_pulse_start3(self):
        return self.read_pulse_start_n(3)

    def read_pulse_stop3(self):
        return self.read_pulse_stop_n(3)

    def read_channel_enable4(self):
        return self.read_channel_n(4)

    def read_pulse_start4(self):
        return self.read_pulse_start_n(4)

    def read_pulse_stop4(self):
        return self.read_pulse_stop_n(4)

    def read_channel_enable5(self):
        return self.read_channel_n(5)

    def read_pulse_start5(self):
        return self.read_pulse_start_n(5)

    def read_pulse_stop5(self):
        return self.read_pulse_stop_n(5)

    def read_channel_enable6(self):
        return self.read_channel_n(6)

    def read_pulse_start6(self):
        return self.read_pulse_start_n(6)

    def read_pulse_stop6(self):
        return self.read_pulse_stop_n(6)

    def read_channel_enable7(self):
        return self.read_channel_n(7)

    def read_pulse_start7(self):
        return self.read_pulse_start_n(7)

    def read_pulse_stop7(self):
        return self.read_pulse_stop_n(7)

    def read_channel_enable8(self):
        return self.read_channel_n(8)

    def read_pulse_start8(self):
        return self.read_pulse_start_n(8)

    def read_pulse_stop8(self):
        return self.read_pulse_stop_n(8)

    def read_channel_enable9(self):
        return self.read_channel_n(9)

    def read_pulse_start9(self):
        return self.read_pulse_start_n(9)

    def read_pulse_stop9(self):
        return self.read_pulse_stop_n(9)

    def read_channel_enable10(self):
        return self.read_channel_n(10)

    def read_pulse_start10(self):
        return self.read_pulse_start_n(10)

    def read_pulse_stop10(self):
        return self.read_pulse_stop_n(10)

    def read_channel_enable11(self):
        return self.read_channel_n(11)

    def read_pulse_start11(self):
        return self.read_pulse_start_n(11)

    def read_pulse_stop11(self):
        return self.read_pulse_stop_n(11)

    # endregion

    # region ---------------- custom attributes write --------------

    def write_auto_rearm(self, v: bool):
        if self.tmr.ready:
            self.set_running()
        else:
            self.set_fault()
        self.config['auto_rearm'] = v
        self.auto_rearm_value = v

    def write_periodic_start(self, v: bool):
        if self.tmr.ready:
            self.set_running()
        else:
            self.set_fault()
        self.config['periodic_start'] = v
        self.periodic_start_value = v

    def write_period(self, v: float):
        if self.tmr.ready:
            self.set_running()
        else:
            self.set_fault()
        self.config['period'] = v
        self.period_value = v

    def write_run(self, value: int):
        result = self.tmr.write_run(value)
        if result:
            self.run.set_value(value)
            self.run.set_quality(AttrQuality.ATTR_VALID)
            self.set_running()
            return True
        self.run.set_quality(AttrQuality.ATTR_INVALID)
        msg = 'Run state write error'
        self.set_fault(msg)
        self.run.set_write_value(0)
        return False

    def write_mode(self, value: int):
        result = self.tmr.write_mode(value)
        if result:
            self.mode.set_value(value)
            self.mode.set_quality(AttrQuality.ATTR_VALID)
            self.set_running()
            self.config['mode'] = value
            return True
        self.mode.set_quality(AttrQuality.ATTR_INVALID)
        msg = 'Mode write error'
        self.set_fault(msg)
        self.mode.set_write_value(0)
        return False

    def write_output(self, value: bool):
        result = self.tmr.write_output(int(value))
        if result:
            self.output.set_value(bool(value))
            self.output.set_quality(AttrQuality.ATTR_VALID)
            self.set_running()
            self.config['output'] = value
            return True
        self.output.set_quality(AttrQuality.ATTR_INVALID)
        msg = 'Output write error'
        self.set_fault(msg)
        self.output.set_write_value(False)
        return False

    def write_duration(self, value: int):
        result = self.tmr.write_duration(int(value))
        if result:
            self.duration.set_value(int(value))
            self.duration.set_quality(AttrQuality.ATTR_VALID)
            self.config['duration'] = int(value)
            self.set_running()
            return True
        self.duration.set_quality(AttrQuality.ATTR_INVALID)
        msg = 'Total duration write error'
        self.set_fault(msg)
        self.duration.set_write_value(0)
        return False

    def write_channel_n(self, n, value):
        result = self.tmr.write_channel_enable(n + 1, int(value))
        name = f'channel_enable{n}'
        if result:
            getattr(self, name).set_value(bool(value))
            getattr(self, name).set_quality(AttrQuality.ATTR_VALID)
            self.set_running()
            self.config[name] = value
            return True
        getattr(self, name).set_quality(AttrQuality.ATTR_INVALID)
        msg = f'Channel {n} state write error'
        self.set_fault(msg)
        getattr(self, name).set_write_value(False)
        return False

    def write_pulse_start_n(self, n, value):
        name = f'pulse_start{n}'
        result = self.tmr.write_channel_start(n + 1, int(value))
        if result:
            getattr(self, name).set_value(int(value))
            getattr(self, name).set_quality(AttrQuality.ATTR_VALID)
            self.set_running()
            self.config[name] = value
            return True
        getattr(self, name).set_quality(AttrQuality.ATTR_INVALID)
        msg = f'Channel {n} start time write error'
        self.set_fault(msg)
        getattr(self, name).set_write_value(0)
        return False

    def write_pulse_stop_n(self, n, value):
        name = f'pulse_stop{n}'
        result = self.tmr.write_channel_stop(n + 1, int(value))
        if result:
            getattr(self, name).set_value(int(value))
            getattr(self, name).set_quality(AttrQuality.ATTR_VALID)
            self.set_running()
            self.config[name] = value
            return True
        getattr(self, name).set_quality(AttrQuality.ATTR_INVALID)
        msg = f'Channel {n} stop time write error'
        self.set_fault(msg)
        getattr(self, name).set_write_value(0)
        return False
    # endregion

    # region ---------------- channels attributes write --------------

    def write_channel_enable0(self, value):
        return self.write_channel_n(0, value)

    def write_pulse_start0(self, value):
        return self.write_pulse_start_n(0, value)

    def write_pulse_stop0(self, value):
        return self.write_pulse_stop_n(0, value)

    def write_channel_enable1(self, value):
        return self.write_channel_n(1, value)

    def write_pulse_start1(self, value):
        return self.write_pulse_start_n(1, value)

    def write_pulse_stop1(self, value):
        return self.write_pulse_stop_n(1, value)

    def write_channel_enable2(self, value):
        return self.write_channel_n(2, value)

    def write_pulse_start2(self, value):
        return self.write_pulse_start_n(2, value)

    def write_pulse_stop2(self, value):
        return self.write_pulse_stop_n(2, value)

    def write_channel_enable3(self, value):
        return self.write_channel_n(3, value)

    def write_pulse_start3(self, value):
        return self.write_pulse_start_n(3, value)

    def write_pulse_stop3(self, value):
        return self.write_pulse_stop_n(3, value)

    def write_channel_enable4(self, value):
        return self.write_channel_n(4, value)

    def write_pulse_start4(self, value):
        return self.write_pulse_start_n(4, value)

    def write_pulse_stop4(self, value):
        return self.write_pulse_stop_n(4, value)

    def write_channel_enable5(self, value):
        return self.write_channel_n(5, value)

    def write_pulse_start5(self, value):
        return self.write_pulse_start_n(5, value)

    def write_pulse_stop5(self, value):
        return self.write_pulse_stop_n(5, value)

    def write_channel_enable6(self, value):
        return self.write_channel_n(6, value)

    def write_pulse_start6(self, value):
        return self.write_pulse_start_n(6, value)

    def write_pulse_stop6(self, value):
        return self.write_pulse_stop_n(6, value)

    def write_channel_enable7(self, value):
        return self.write_channel_n(7, value)

    def write_pulse_start7(self, value):
        return self.write_pulse_start_n(7, value)

    def write_pulse_stop7(self, value):
        return self.write_pulse_stop_n(7, value)

    def write_channel_enable8(self, value):
        return self.write_channel_n(8, value)

    def write_pulse_start8(self, value):
        return self.write_pulse_start_n(8, value)

    def write_pulse_stop8(self, value):
        return self.write_pulse_stop_n(8, value)

    def write_channel_enable9(self, value):
        return self.write_channel_n(9, value)

    def write_pulse_start9(self, value):
        return self.write_pulse_start_n(9, value)

    def write_pulse_stop9(self, value):
        return self.write_pulse_stop_n(9, value)

    def write_channel_enable10(self, value):
        return self.write_channel_n(10, value)

    def write_pulse_start10(self, value):
        return self.write_pulse_start_n(10, value)

    def write_pulse_stop10(self, value):
        return self.write_pulse_stop_n(10, value)

    def write_channel_enable11(self, value):
        return self.write_channel_n(11, value)

    def write_pulse_start11(self, value):
        return self.write_pulse_start_n(11, value)

    def write_pulse_stop11(self, value):
        return self.write_pulse_stop_n(11, value)

    # endregion

    # region ---------------- custom commands --------------

    @command(dtype_in=None, doc_in='Start timer pulse',
             dtype_out=bool, doc_out='True if success')
    def start_pulse(self):
        result = self.tmr.write_run(3)
        if result == 1:
            result = self.tmr.write_run(0)
            result = self.tmr.write_run(1)
            self.last_time_value = time.time()
            if result == 1:
                if self.read_duration() > 100:
                    result = self.read_pulse()
                if result == 1:
                    self.info('Pulse has been started at %s', self.last_time_value)
                    self.set_running()
                    return True
        msg = f'Start pulse error {self.tmr.error}'
        self.set_fault(msg)
        return False

    @command(dtype_in=None, doc_in='Start timer pulse',
             dtype_out=bool, doc_out='True if success')
    def stop_pulse(self):
        result = self.tmr.write_run(0)
        if result == 1:
            result = self.read_pulse()
            if result == 0:
                self.set_running()
                return True
        msg = f'Stop Pulse Error {self.tmr.error}'
        self.set_fault(msg)
        return False

    @command(dtype_in=None, doc_in='Prepare for external trigger',
             dtype_out=bool, doc_out='True if success')
    def get_ready(self):
        result = self.read_pulse()
        if result:
            self.info('Can not arm. Pulse in progress. Stop pulse first')
            return False
        result = self.tmr.write_run(3)
        if result == 1:
            result = self.tmr.write_run(0)
            if result == 1:
                result = self.tmr.write_run(2)
                if result == 1:
                    self.ready = True
                    self.info('Ready for Pulse')
                    self.set_running()
                    return True
        self.ready = False
        msg = f'External Trigger Arm Error {self.tmr.error}'
        self.set_fault(msg)
        return False

    @command(dtype_in=int, doc_in='Fast read channel data',
             dtype_out=[int], doc_out='[Enable, Start, Stop]; [] if error')
    def read_channel(self, n):
        result = self.tmr.read_channel(n + 1)
        if result:
            self.set_running()
            return result
        msg = f'Read channel {n} error {self.tmr.error}'
        self.set_fault(msg)
        return []

    @command(dtype_in=None, doc_in='Save current timer state',
             dtype_out=None)
    def save_state(self):
        self.write_config_to_properties()

    @command(dtype_in=None, doc_in='Restore timer state',
             dtype_out=bool)
    def restore_state(self):
        try:
            self.read_config_from_properties()
            self.write_mode(self.config['mode'])
            self.write_output(self.config['output'])
            self.write_duration(self.config['duration'])
            for n in range(0, 12):
                aname = f'channel_enable{n}'
                setattr(self, aname, self.config[aname])
                aname = f'channel_start{n}'
                setattr(self, aname, self.config[aname])
                aname = f'channel_stop{n}'
                setattr(self, aname, self.config[aname])
            self.run.set_write_value(self.run)
            self.mode.set_write_value(self.mode)
            self.output.set_write_value(self.output)
            self.period.set_write_value(self.period)
            self.duration.set_write_value(self.duration)
            self.periodic_start.set_write_value(self.periodic_start)
            self.auto_rearm.set_write_value(self.auto_rearm)
            self.restore_state.set_write_value(self.restore_state)
            self.info('State restored')
            return True
        except:
            self.error('State restore error')
            return False
    # endregion


def looping():
    for dn in TangoServerPrototype.devices:
        dev = TangoServerPrototype.devices[dn]
        if dev.auto_rearm:
            if not dev.pulse:
                dev.get_ready()
        # if dev.periodic_start_value and dev.period_value > 0.0:
            # if dev.last_time_value + dev.period_value < time.time():
                # dev.start_pulse()
                # dev.last_time_value = time.time()
                # print('Pulse')
    time.sleep(0.1)


if __name__ == "__main__":
    VtimerServer.run_server(event_loop=looping)
