import os
import sys
import time

_u = os.path.dirname(os.path.realpath(sys.argv[0]))
_util_path = os.path.join(os.path.split(_u)[0], 'TangoUtils')
if _util_path not in sys.path: sys.path.append(_util_path)
del _u, _util_path

from ModbusDevice import ModbusDevice

import time
from functools import wraps


def timeit(func):
    """Decorator that prints the elapsed time of a function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # Record start time
        result = func(*args, **kwargs)  # Execute function
        end_time = time.perf_counter()  # Record end time

        elapsed_time = end_time - start_time
        print(f"Function '{func.__name__}' took {elapsed_time:.6f} seconds to execute.")
        return result

    return wrapper


APPLICATION_NAME = 'Vtimer I/O modules Python API'
APPLICATION_NAME_SHORT = 'Vtimer'
APPLICATION_VERSION = '1.2'
ELAPSED = 0.0

class Vtimer(ModbusDevice):
    def __init__(self, port: str, addr: int, **kwargs):
        super().__init__(port, addr, **kwargs)
        self.read_time = [0.0]*13
        self.read_data = [0]*13
        self.read_valid_time = 0.5
        self.id = 'Timer'
        self.pre = f'{self.id} at {self.port}:{self.addr} '
        self.config = {'settings': [0, 0, 0, 1, 1], 'channels': [[0, 0, 0, 0, 1, 0, 1, 1] for i in range(13)]}
        errors = 0
        if not hasattr(self, 'initialized'):
            self.initialized = False
            self.start = [0] * 12
            self.stop = [1] * 12
            self.enable = [0] * 12
            self.duration = 1
            self.mode = 0
            self.output = 1
        v = self.modbus_write(0, self.config['settings'])
        if v != 5:
            self.info(f'Settings initialization error')
            errors += 1
        for i in range(1, 13):
            # self.debug(f'Initializing {i} {len(self.config['channels'])}')
            v = self.modbus_write(16 * i, self.config['channels'][i])
            if v != 8:
                self.info(f'Channel {i} initialization error')
                errors += 1
        if errors == 0:
            self.initialized = True
            self.info('initialized')
        else:
            self.initialized = False
            self.warning('initialized with errors')

    @property
    def ready(self):
        t0 = time.time()
        if t0 < self.suspend_to:
            # self.debug(f"Suspended for {self.suspend_to - t0} seconds")
            return False
        # was suspended, try to init
        if self.suspend_to > 0.0:
            self.__del__()
            self.__init__(self.port, self.addr, **self.kwargs)
            if self.initialized:
                self.write_duration(self.duration)
                self.write_mode(self.mode)
                for i in range(12):
                    self.write_channel_stop(i + 1, self.stop[i])
                    self.write_channel_start(i + 1, self.start[i])
                    self.write_channel_enable(i + 1, self.enable[i])
        return self.suspend_to <= 0.0

    def read_channel_start(self, n: int) -> int:
        with self.com.lock:
            delay = self.modbus_read(16 * n + 1, 2)
            if delay:
                v = delay[0] * 0x10000 + delay[1]
                self.start[n - 1] = v
                return v
            return -1

    def read_channel_stop(self, n: int) -> int:
        with self.com.lock:
            delay = self.modbus_read(16 * n + 3, 2)
            if delay:
                v = delay[0] * 0x10000 + delay[1]
                self.stop[n - 1] = v
                return v
            return -1

    # def modbus_read(self, start: int, length: int=1, address=None, command=3):
    #     old = super().modbus_read(start, length, address, command)
    #     n = 8
    #     if start < 16:
    #         n = 9
    #         # return super().modbus_read(start, length, address, command)
    #     index = start // 16
    #     if time.time() - self.read_time[index] < self.read_valid_time:
    #         result = self.read_data[index]
    #     else:
    #         result = super().modbus_read(index * 16, n, address, command)
    #         self.read_data[index] = result
    #         self.read_time[index] = time.time()
    #     first = start % 16
    #     new = result[first:first+length]
    #     if new != old:
    #         print("Mismatch", old, new)
    #         return old
    #     return new

    def read_channel_enable(self, n: int) -> int:
        with self.com.lock:
            data = self.modbus_read(16 * n, 1)
            if data:
                self.enable[n - 1] = data[0]
                return data[0]
            else:
                return -1

    def read_channel(self, n: int) -> [int]:
        with self.com.lock:
            result = self.modbus_read(16 * n, 5)
            if len(result) != 5:
                return []
            s1 = result[0]
            self.enable[n - 1] = s1
            s2 = result[1] * 0x10000 + result[2]
            self.start[n - 1] = s2
            s3 = result[3] * 0x10000 + result[4]
            self.stop[n - 1] = s3
            return [s1, s2, s3]

    def read_run(self) -> int:
        with self.com.lock:
            data = self.modbus_read(0, 1)
            if data:
                return data[0]
            else:
                return -1

    def read_mode(self) -> int:
        with self.com.lock:
            data = self.modbus_read(1, 1)
            if data:
                self.mode = data[0]
                return data[0]
            else:
                return -1

    def read_status(self) -> int:
        with self.com.lock:
            data = self.modbus_read(5, 1)
            if data:
                return data[0]
            else:
                # self.debug(' Status register read error')
                return -1

    def read_output(self) -> int:
        with self.com.lock:
            data = self.modbus_read(4, 1)
            if data:
                self.output = data[0]
                return data[0]
            else:
                # self.debug(' Output register read error')
                return -1

    def read_fault(self) -> int:
        with self.com.lock:
            data = self.modbus_read(1, 1)
            if data:
                return data[0]
            else:
                # self.debug(' Fault register read error')
                return -1

    def read_duration(self) -> int:
        with self.com.lock:
            data = self.modbus_read(2, 2)
            if data:
                v = data[0] * 0x10000 + data[1]
                self.duration = v
                return v
            else:
                # self.debug(' Script duration read error')
                return -1

    def read_last(self) -> int:
        with self.com.lock:
            data = self.modbus_read(7, 2)
            if data:
                return data[0] * 65536 + data[1]
            else:
                # self.debug(' Last pulse duration read error')
                return -1

    def write_channel_start(self, n: int, v: int) -> bool:
        with self.com.lock:
            # print('write_channel_start', n, v)
            delay = [0, 0]
            delay[0] = v // 0x10000
            delay[1] = v % 0x10000
            result = self.modbus_write(16 * n + 1, delay)
            # print('write_channel_start',result)
            if result != 2:
                return False
            self.start[n - 1] = v
            return True

    def write_channel_stop(self, n: int, v: int) -> bool:
        with self.com.lock:
            # print('write_channel_stop', n, v)
            delay = [0, 0]
            delay[0] = v // 0x10000
            delay[1] = v % 0x10000
            result = self.modbus_write(16 * n + 3, delay)
            # print('write_channel_stop result', result)
            if result != 2:
                return False
            self.stop[n - 1] = v
            ms = max(self.stop)
            if self.duration != ms:
                return self.write_duration(ms)
            return True

    def write_channel_enable(self, n: int, v: int) -> bool:
        with self.com.lock:
            result = self.modbus_write(16 * n, int(bool(v)))
            if result != 1:
                return False
            self.enable[n - 1] = v
            return True

    def enable_channel(self, n: int) -> bool:
        with self.com.lock:
            return self.write_channel_enable(n, 1)

    def disable_channel(self, n: int) -> bool:
        with self.com.lock:
            return self.write_channel_enable(n, 0)

    def write_run(self, n: int) -> bool:
        with self.com.lock:
            m = self.modbus_write(0, n)
            return m == 1

    def write_mode(self, n: int) -> bool:
        with self.com.lock:
            result = self.modbus_write(1, n)
            if result != 1:
                return False
            self.mode = n
            return True

    def write_output(self, n: int) -> bool:
        with self.com.lock:
            result = self.modbus_write(4, n)
            if result != 1:
                return False
            self.output = n
            return True

    def write_duration(self, n: int) -> bool:
        with self.com.lock:
            v = [0, 0]
            v[0] = n // 0x10000
            v[1] = n % 0x10000
            result = self.modbus_write(2, v)
            if result != 2:
                return False
            self.duration = n
            return True

class VirtualVtimer(ModbusDevice):
    def __init__(self, port: str = 'none', addr: int = 0, **kwargs):
        self.port = port
        self.addr = addr
        self.kwargs = kwargs
        self.id = 'Virtual Timer'
        self.pre = f'{self.id} at {self.port}: {self.addr} '
        self.config = {'settings': [0, 0, 0, 1, 1], 'channels': [[0, 0, 0, 0, 1, 0, 1, 1] for i in range(13)]}
        errors = 0
        if not hasattr(self, 'initialized'):
            self.initialized = False
            self.start = [0] * 12
            self.stop = [1] * 12
            self.enable = [0] * 12
            self.duration = 1
            self.mode = 0
            self.output = 1
        v = self.modbus_write(0, self.config['settings'])
        if v != 5:
            self.debug(f'Settings initialization error')
            errors += 1
        for i in range(1, 13):
            v = self.modbus_write(16 * i, self.config['channels'][i])
            if v != 8:
                self.debug(f'Channel {i} initialization error')
                errors += 1
        if errors == 0:
            self.initialized = True
            self.info('has been initialized')
        else:
            self.initialized = False
            self.info('has been initialized with errors')

    @property
    def ready(self):
        with self.com.lock:
            t0 = time.time()
            if t0 < self.suspend_to:
                # self.debug(f"Suspended for {self.suspend_to - t0} seconds")
                return False
            # was suspended, try to init
            if self.suspend_to > 0.0:
                self.__del__()
                self.__init__(self.port, self.addr, **self.kwargs)
                if self.initialized:
                    self.write_duration(self.duration)
                    self.write_mode(self.mode)
                    for i in range(12):
                        self.write_channel_stop(i + 1, self.stop[i])
                        self.write_channel_start(i + 1, self.start[i])
                        self.write_channel_enable(i + 1, self.enable[i])
            return self.suspend_to <= 0.0

    def read_channel_start(self, n: int) -> int:
        with self.com.lock:
            delay = self.modbus_read(16 * n + 1, 2)
            if delay:
                v = delay[0] * 0x10000 + delay[1]
                self.start[n - 1] = v
                return v
            return -1

    def read_channel_stop(self, n: int) -> int:
        with self.com.lock:
            delay = self.modbus_read(16 * n + 3, 2)
            if delay:
                v = delay[0] * 0x10000 + delay[1]
                self.stop[n - 1] = v
                return v
            return -1

    def read_channel_enable(self, n: int) -> int:
        with self.com.lock:
            data = self.modbus_read(16 * n, 1)
            if data:
                self.enable[n - 1] = data[0]
                return data[0]
            else:
                return -1

    def read_channel(self, n: int) -> [int]:
        with self.com.lock:
            result = self.modbus_read(16 * n, 5)
            if len(result) != 5:
                return []
            s1 = result[0]
            self.enable[n - 1] = s1
            s2 = result[1] * 0x10000 + result[2]
            self.start[n - 1] = s2
            s3 = result[3] * 0x10000 + result[4]
            self.stop[n - 1] = s3
            return [s1, s2, s3]

    def read_run(self) -> int:
        with self.com.lock:
            data = self.modbus_read(0, 1)
            if data:
                return data[0]
            else:
                return -1

    def read_mode(self) -> int:
        with self.com.lock:
            data = self.modbus_read(1, 1)
            if data:
                self.mode = data[0]
                return data[0]
            else:
                return -1

    def read_status(self) -> int:
        with self.com.lock:
            data = self.modbus_read(5, 1)
            if data:
                return data[0]
            else:
                # self.debug(' Status register read error')
                return -1

    def read_output(self) -> int:
        with self.com.lock:
            data = self.modbus_read(4, 1)
            if data:
                self.output = data[0]
                return data[0]
            else:
                # self.debug(' Output register read error')
                return -1

    def read_fault(self) -> int:
        with self.com.lock:
            data = self.modbus_read(1, 1)
            if data:
                return data[0]
            else:
                # self.debug(' Fault register read error')
                return -1

    def read_duration(self) -> int:
        with self.com.lock:
            data = self.modbus_read(2, 2)
            if data:
                v = data[0] * 0x10000 + data[1]
                self.duration = v
                return v
            else:
                # self.debug(' Script duration read error')
                return -1

    def read_last(self) -> int:
        with self.com.lock:
            data = self.modbus_read(7, 2)
            if data:
                return data[0] * 65536 + data[1]
            else:
                # self.debug(' Last pulse duration read error')
                return -1

    def write_channel_start(self, n: int, v: int) -> bool:
        with self.com.lock:
            delay = [0, 0]
            delay[0] = v // 0x10000
            delay[1] = v % 0x10000
            result = self.modbus_write(16 * n + 1, delay)
            if result != 2:
                return False
            self.start[n - 1] = v
            return True

    def write_channel_stop(self, n: int, v: int) -> bool:
        with self.com.lock:
            delay = [0, 0]
            delay[0] = v // 0x10000
            delay[1] = v % 0x10000
            result = self.modbus_write(16 * n + 3, delay)
            if result != 2:
                return False
            self.stop[n - 1] = v
            ms = max(self.stop)
            if self.duration != ms:
                return self.write_duration(ms)
            return True

    def write_channel_enable(self, n: int, v: int) -> bool:
        with self.com.lock:
            result = self.modbus_write(16 * n, int(bool(v)))
            if result != 1:
                return False
            self.enable[n - 1] = v
            return True

    def enable_channel(self, n: int) -> bool:
        with self.com.lock:
            return self.write_channel_enable(n, 1)

    def disable_channel(self, n: int) -> bool:
        with self.com.lock:
            return self.write_channel_enable(n, 0)

    def write_run(self, n: int) -> bool:
        with self.com.lock:
            m = self.modbus_write(0, n)
            return m == 1

    def write_mode(self, n: int) -> bool:
        with self.com.lock:
            result = self.modbus_write(1, n)
            if result != 1:
                return False
            self.mode = n
            return True

    def write_output(self, n: int) -> bool:
        with self.com.lock:
            result = self.modbus_write(4, n)
            if result != 1:
                return False
            self.output = n
            return True

    def write_duration(self, n: int) -> bool:
        with self.com.lock:
            v = [0, 0]
            v[0] = n // 0x10000
            v[1] = n % 0x10000
            result = self.modbus_write(2, v)
            if result != 2:
                return False
            self.duration = n
            return True

if __name__ == "__main__":
    try:
        port = sys.argv[1]
    except:
        port = "COM4"
    try:
        addr = sys.argv[2]
    except:
        addr = 1

    ot1 = Vtimer(port, addr)

    t_0 = time.time()

    n = 100
    t_0 = time.time()
    for i in range(n):
        v = ot1.read_run()
    dt = int((time.time() - t_0) * 1000.0)  # ms
    a = '%s:%s %s %s %s' % (ot1.port, ot1.addr, 'read_run->', v, '%4d ms ' % dt/n)
    print(a)
    print('')

    n = 100
    t_0 = time.time()
    for i in range(n):
        v = ot1.write_channel_stop(1, 100)
    dt = ((time.time() - t_0) * 1000.0)  # ms
    a = f'{ot1.port}:{ot1.addr} {n}x write_stop(1) -> {v} average {dt/n} ms'
    print(a)
    print('')

    n = 100
    t_0 = time.time()
    for i in range(n):
        v = ot1.read_channel_start(1)
    dt = ((time.time() - t_0) * 1000.0)  # ms
    a = f'{ot1.port}:{ot1.addr} {n}x read_start(1)-> {v} average {dt/n} ms'
    print(a)
    print('')

    n = 100
    t_0 = time.time()
    for i in range(n):
        v = ot1.read_channel_stop(1)
    dt = ((time.time() - t_0) * 1000.0)  # ms
    a = f'{ot1.port}:{ot1.addr} {n}x read_stop(1)-> {v} average {dt/n} ms'
    print(a)
    print('')

    t_0 = time.time()
    n = 1
    v0 = ot1.write_output(1)
    # v1 = ot1.write_duration(12 * n + 1)
    for i in range(1, 13):
        v3 = ot1.write_channel_stop(i, i * n)
        v2 = ot1.write_channel_start(i, (i - 1) * n)
        v6 = ot1.enable_channel(i)
    v8 = ot1.write_run(3)
    v = ot1.write_run(1)
    f = ot1.read_fault()
    # while ot1.read_status():
    #     pass
    l = ot1.read_last()

    dt = int((time.time() - t_0) * 1000.0)  # ms
    a = '%s:%s %s %s %s %s %s' % (ot1.port, ot1.addr, '->', v, f, l, '%4d ms ' % dt)
    print(a)
    print('')

    print('Finished')
