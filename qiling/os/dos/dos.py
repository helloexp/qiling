import types, os, struct

from unicorn import *
from qiling.os.os import QlOs
from qiling.os.utils import PathUtils
from qiling.exception import QlErrorSyscallError
from enum import Enum
import curses
import curses.ascii

# Modified from https://programtalk.com/vs2/python/8562/pyvbox/virtualbox/library_ext/keyboard.py/
SCANCODES = {
    curses.KEY_A1:    0x01,
    ord('1'):      0x02, ord('!'): 0x02,
    ord('2'):      0x03, ord('@'): 0x03,
    ord('3'):      0x04, ord('#'): 0x04,
    ord('4'):      0x05, ord('$'): 0x05,
    ord('5'):      0x06, ord('%'): 0x06,
    ord('6'):      0x07, ord('^'): 0x07,
    ord('7'):      0x08, ord('&'): 0x07,
    ord('8'):      0x09, ord('*'): 0x09,
    ord('9'):      0x0A, ord('('): 0x0A,
    ord('0'):      0x0B, ord(')'): 0x0B,
    ord('-'):      0x0C, ord('_'): 0x0C,
    ord('='):      0x0D, ord('+'): 0x0D,
    curses.KEY_BACKSPACE:   0x0E,                 
    ord('\b'):     0x0E,              
    ord('\t'):     0x0F,                  
    ord('q'):      0x10, ord('Q'): 0x10,
    ord('w'):      0x11, ord('W'): 0x11,
    ord('e'):      0x12, ord('E'): 0x12,
    ord('r'):      0x13, ord('R'): 0x13,
    ord('t'):      0x14, ord('T'): 0x14,
    ord('y'):      0x15, ord('Y'): 0x15,
    ord('u'):      0x16, ord('U'): 0x16,
    ord('i'):      0x17, ord('I'): 0x17,
    ord('o'):      0x18, ord('O'): 0x18,
    ord('p'):      0x19, ord('P'): 0x19,
    ord('['):      0x1A, ord('}'): 0x1A,
    ord(']'):      0x1B, ord('{'): 0x1B,
    curses.KEY_ENTER:  0x1C, 
    ord('\r'):     0x1C, 
    ord('\n'):     0x1C,
    curses.KEY_C1:   0x1D,
    ord('a'):      0x1E, ord('A'): 0x1E,
    ord('s'):      0x1F, ord('S'): 0x1F,
    ord('d'):      0x20, ord('D'): 0x20,
    ord('f'):      0x21, ord('F'): 0x21,
    ord('g'):      0x22, ord('G'): 0x22,
    ord('h'):      0x23, ord('H'): 0x23,
    ord('j'):      0x24, ord('J'): 0x24,
    ord('k'):      0x25, ord('K'): 0x25,
    ord('l'):      0x26, ord('L'): 0x26,
    ord(';'):      0x27, ord(':'): 0x27,
    ord('\''):     0x28, ord('\"'):0x28,
    ord('`'):      0x29, ord('~'): 0x29,
    #'SHIFT': [[0x2A], [0xAA]], it seems hard to support shift.
    ord('\\'):     0x2B, ord('|'): 0x2B,
    ord('z'):      0x2C, ord('Z'): 0x2C,
    ord('x'):      0x2D, ord('X'): 0x2D,
    ord('c'):      0x2E, ord('C'): 0x2E,
    ord('v'):      0x2F, ord('V'): 0x2F,
    ord('b'):      0x30, ord('B'): 0x30,
    ord('n'):      0x31, ord('N'): 0x31,
    ord('m'):      0x32, ord('M'): 0x32,
    ord(','):      0x33, ord('<'): 0x33,
    ord('.'):      0x34, ord('>'): 0x34,
    ord('/'):      0x35, ord('?'): 0x35,
    #'RSHIFT': [[0x36], [0xB6]],
    curses.KEY_PRINT:  0x37,
    #'ALT':    [[0x38], [0xB8]],
    ord(' '):      0x39,
    #'CAPS':   [[0x3A], [0xBA]],
    curses.KEY_F1:     0x3B, 
    curses.KEY_F2:     0x3C, 
    curses.KEY_F3:     0x3D, 
    curses.KEY_F4:     0x3E, 
    curses.KEY_F5:     0x3F, 
    curses.KEY_F6:     0x40, 
    curses.KEY_F7:     0x41, 
    curses.KEY_F8:     0x42, 
    curses.KEY_F9:     0x43, 
    curses.KEY_F10:    0x44, 
    curses.KEY_F11:    0x57, 
    curses.KEY_F12:    0x58, 
    #'NUM':    [[0x45], [0xC5]], 
    #'SCRL':   [[0x46], [0xC6]], 
    curses.KEY_HOME:   0x47, 
    curses.KEY_UP:     0x48, 
    curses.KEY_PPAGE:   0x49, 
    #'MINUS':  [[0x4A], [0xCA]], 
    curses.KEY_LEFT:   0x4B, 
    curses.KEY_B2: 0x4C, 
    curses.KEY_RIGHT:  0x4D, 
    #'PLUS':   [[0x4E], [0xCE]], 
    curses.KEY_END:    0x4F, 
    curses.KEY_DOWN:   0x50, 
    curses.KEY_NPAGE:   0x51, 
    curses.KEY_IC:    0x52, 
    curses.KEY_DC:    0x53,
    #'E_DIV':  [[0xE0, 0x54], [0xE0, 0xD4]], 
    #'E_ENTER':[[0xE0, 0x1C], [0xE0, 0x9C]],
    #'E_INS':  [[0xE0, 0x52], [0xE0, 0xD2]],
    #'E_DEL':  [[0xE0, 0x53], [0xE0, 0xD3]],
    #'E_HOME': [[0xE0, 0x47], [0xE0, 0xC7]], 
    #'E_END':  [[0xE0, 0x4F], [0xE0, 0xCF]], 
    #'E_PGUP': [[0xE0, 0x49], [0xE0, 0xC9]], 
    #'E_PGDN': [[0xE0, 0x51], [0xE0, 0xD1]], 
    #'E_LEFT': [[0xE0, 0x4B], [0xE0, 0xCB]], 
    #'E_RIGHT':[[0xE0, 0x4D], [0xE0, 0xCD]], 
    #'E_UP':   [[0xE0, 0x48], [0xE0, 0xC8]], 
    #'E_DOWN': [[0xE0, 0x50], [0xE0, 0xD0]], 
    #'RALT':   [[0x0C, 0x38], [0xC0, 0xB8]], 
    #'RCTRL':  [[0x0C, 0x1D], [0xC0, 0x9D]], 
    #'LWIN':   [[0xE0, 0x5B], [0xE0, 0xDB]], 
    #'RWIN':   [[0xE0, 0x5C], [0xE0, 0xDC]], 
    # No scan code for pause key released
    #'PAUSE':  [[0xE1, 0x1D, 0x45, 0xE1, 0x9D, 0xC5], []],
}


class INT13DiskError(Enum):
    NoError = 0
    BadCommand = 1
    AddressNotFound = 2
    DiskWriteProtectError = 3
    SectorNotFound = 4
    FixedDiskResetFailed = 5
    DiskChangedOrRemoved = 6
    BadFixedDiskParameterTable = 7
    DMAOverrun = 8
    DMAAcessAcrossBoundary = 9
    BadFixedDiskSectorFlag = 10
    BadFixedDiskCylinder = 11
    UnsupportedTrack = 12
    InvalidNumberofSectors = 13
    FixedDiskControlledDataAdressDetected = 14
    FixedDiskDMAArbitrationLevelOutofRange = 15
    ECCErrorOnRead = 16
    RecoverableFixedDiskDataError = 17
    ControllerError = 32
    SeekFailure = 64
    Timeout = 128
    FixedDiskDriveNotReady = 170
    FixedDiskUndefinedError = 187
    FixedDiskWriteFault = 204
    FixedDiskStatusError = 224
    SenseOperationFailed = 255

class QlOsDos(QlOs):
    def __init__(self, ql):
        super(QlOsDos, self).__init__(ql)
        self.ql = ql
        self.hook_syscall()
        self.handle_next = 0
        self.dos_handles = {}
        self.stdscr = None
    
    def __del__(self):
        # resume terminal
        if self.stdscr is not None:
            self.stdscr.keypad(0)
            curses.echo()
            curses.nocbreak()
            curses.endwin()

    # https://en.wikipedia.org/wiki/FLAGS_register
    # 0  CF 0x0001
    # 2  PF 0x0004
    # 4  AF 0x0010
    # 6  ZF 0x0040
    # 7  SF 0x0080
    # 8  TF 0x0100
    # 9  IF 0x0200
    # 10 DF 0x0400
    # 11 OF 0x0800
    # 12-13 IOPL 0x3000
    # 14 NT 0x4000
    def set_flag(self, fl):
        self.ql.reg.ef = self.ql.reg.ef | fl
    
    def clear_flag(self, fl):
        self.ql.reg.ef = self.ql.reg.ef & (~fl)
    
    def test_flags(self, fl):
        return self.ql.reg.ef & fl == fl

    def set_cf(self):
        self.set_flag(0x1)

    def clear_cf(self):
        self.clear_flag(0x1)

    def calculate_address(self, sg, reg):
        return sg*16 + reg

    def read_dos_string(self, addr):
        str_address = addr
        s = ""
        while True:
            ch = chr(self.ql.mem.read(str_address, 1)[0])
            if ch == '$':
                break
            s += ch
            str_address += 1
        return s

    def read_dos_string_from_ds_dx(self):
        return self.read_dos_string(self.calculate_address(self.ql.reg.ds, self.ql.reg.dx))

    def _parse_dap(self, dapbs):
        return struct.unpack("<BBHHHQ", dapbs)

    def int10(self):
        # BIOS video support
        # https://en.wikipedia.org/wiki/INT_10H
        # https://stanislavs.org/helppc/idx_interrupt.html
        # implemented by curses
        ah = self.ql.reg.ah
        al = self.ql.reg.al
        if ah==0:
            # time to set up curses
            # copied from curses.wrapper
            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(1)
            try:
                curses.start_color()
            except:
                pass
            if al == 0 or al == 1:
                curses.resizeterm(25, 40)
            elif al == 2 or al == 3:
                curses.resizeterm(25, 80)
            elif al == 4 or al == 5:
                curses.resizeterm(200, 320)
            elif al == 6:
                curses.resizeterm(200, 640)
            else:
                raise NotImplementedError()
            self.stdscr.scrollok(True)
                
            if al in [1, 3, 5] and not curses.has_colors():
                self.ql.nprint(f"[!] Warning: your terminal doesn't support colors, content might not be displayed correctly.")
        elif ah == 1:
            # limited support
            ch = self.ql.reg.ch
            if (ch & 0x20) != 0:
                curses.curs_set(0)
        elif ah == 2:
            # page number ignored
            dh = self.ql.reg.dh # row
            dl = self.ql.reg.dl # column
            self.stdscr.move(dh, dl)
        elif ah == 5:
            # No idea how to implement, do nothing here.
            self.ql.reg.al = 0
            pass
        elif ah == 6:
            al = self.ql.reg.al # lines to scroll
            ch = self.ql.reg.ch # row of upper-left cornner
            cl = self.ql.reg.cl # column of upper-left corner
            dh = self.ql.reg.dh # row of lower right corner
            dl = self.ql.reg.dl # column of lower righ corner
            y, x = self.stdscr.getmaxyx()
            if ch != 0 or cl != 0 or dh != y - 1 or dl != x - 1:
                self.ql.nprint(f"[!] Warning: Partial scroll is unsupported. Will scroll the whole page.")
                self.ql.nprint(f"[!] Resolution: {y}x{x} but asked to scroll [({ch},{cl}),({dh}, {dl})]")
            if al != 0:
                self.stdscr.scroll(al)
            else:
                self.stdscr.clear()
        elif ah == 8:
            # page number ignored
            ch = self.stdscr.getch()
            self.ql.reg.ah = 0
            self.ql.reg.al = ch
        elif ah == 0xE:
            self.ql.nprint(f"Echo: {hex(al)} -> {curses.ascii.unctrl(al)}")
            if al == 0xa:
                # \n will erase current line with echochar, so we have to handle it carefully.
                y, x = self.stdscr.getmaxyx()
                cy, cx = self.stdscr.getyx()
                self.ql.nprint(f"Resolution: {x}x{y}, Cursor position: {cx},{cy}, Goint to get a new line.")
                if y-1 == cy:
                    self.stdscr.scroll(1)
                self.stdscr.move(cy+1, 0)
            else:
                self.stdscr.echochar(al)
        else:
            raise NotImplementedError()
        self.stdscr.refresh()

    def int13(self):
        ah = self.ql.reg.ah
        ds = self.ql.reg.ds
        si = self.ql.reg.si
        # https://en.wikipedia.org/wiki/INT_13H
        if ah == 0x0:
            self.ql.reg.ah = 0
            self.clear_cf()
        elif ah == 0x8:
            # https://stanislavs.org/helppc/int_13-8.html
            idx = self.ql.reg.dl
            if not self.ql.os.fs_mapper.has_mapping(idx):
                self.ql.nprint(f"[!] Warning: No such disk: {hex(idx)}")
                self.ql.reg.ah = INT13DiskError.BadCommand.value
                self.set_cf()
                return
            disk = self.ql.os.fs_mapper.open(idx, None)
            self.ql.reg.dl = self.ql.os.fs_mapper.mapping_count()
            self.ql.reg.dh = disk.n_heads - 1
            self.ql.reg.bl = 0x4
            self.ql.reg.di = 0
            self.ql.reg.ds = 0
            if disk.n_sectors > 63:
                n_sectors = 63
            else:
                n_sectors = disk.n_sectors
            if disk.n_cylinders > 1023:
                n_cylinders = 1023
            else:
                n_cylinders = disk.n_cylinders
            cx = 0 | (n_sectors & 0b111111)
            cx = cx | ( (n_cylinders & 0b11) << 6)
            cx = cx | (  ((n_cylinders & 0b1111111100) >> 2) << 8 )
            self.ql.reg.cx = cx
            self.ql.reg.ah = 0
            self.clear_cf()
            pass
        elif ah == 0x42:
            idx = self.ql.reg.dl
            dapbs = self.ql.mem.read(self.calculate_address(ds, si), 0x10)
            _, _, cnt, offset, segment, lba = self._parse_dap(dapbs)
            self.ql.nprint(f"Reading from disk {hex(idx)} with LBA {lba}")
            if not self.ql.os.fs_mapper.has_mapping(idx):
                self.ql.nprint(f"[!] Warning: No such disk: {hex(idx)}")
                self.ql.reg.ah = INT13DiskError.BadCommand.value
                self.set_cf()
                return
            disk = self.ql.os.fs_mapper.open(idx, None)
            content = disk.read_sectors(lba, cnt)
            self.ql.mem.write(self.calculate_address(segment, offset), content)
            self.clear_cf()
            self.ql.reg.ah = 0
        else:
            raise NotImplementedError()

    def int16(self):
        ah = self.ql.reg.ah
        if ah == 0x1:
            # set non-blocking
            self.stdscr.timeout(0)
            key = self.stdscr.getch()
            self.ql.dprint(0, f"Get key: {hex(key)} ({curses.ascii.unctrl(key)})")
            if key == -1:
                self.set_flag(0x40)
                self.ql.reg.ax = 0
            else:
                self.ql.reg.al = key
                if key in SCANCODES:
                    self.ql.reg.ah = SCANCODES[key]
                else:
                    self.ql.nprint(f"[!] Warning: scan code for {hex(key)} doesn't exist!")
                    self.ql.reg.ah = 0
                self.clear_flag(0x40)
            self.stdscr.timeout(-1)

    def int1a(self):
        ah = self.ql.reg.ah
        if ah == 0:
            self.ql.reg.al=0
            self.ql.reg.cx=0
            self.ql.reg.dx=0

    def int21(self):
        ah = self.ql.reg.ah
        if ah == 0x4C:
            self.ql.uc.emu_stop()
        elif ah == 0x2 or ah == 0x6:
            ch = chr(self.ql.reg.dl)
            self.ql.reg.al = self.ql.reg.dl
            self.ql.nprint(ch)
        elif ah == 0x9:
            s = self.read_dos_string_from_ds_dx()
            self.ql.nprint(s)
        elif ah == 0x3C:
            # fileattr ignored
            fname = self.read_dos_string_from_ds_dx()
            f = open(PathUtils.convert_for_native_os(self.ql.rootfs, self.ql.cur_path, fname), "wb")
            self.dos_handles[self.handle_next] = f
            self.ql.reg.ax = self.handle_next
            self.handle_next += 1
            self.clear_cf()
        elif ah == 0x3d:
            fname = self.read_dos_string_from_ds_dx()
            f = open(PathUtils.convert_for_native_os(self.ql.rootfs, self.ql.cur_path, fname), "rb")
            self.dos_handles[self.handle_next] = f
            self.ql.reg.ax = self.handle_next
            self.handle_next += 1
            self.clear_cf()
        elif ah == 0x3e:
            hd = self.ql.reg.bx
            if hd not in self.dos_handles:
                self.ql.reg.ax = 0x6
                self.set_cf()
            else:
                f = self.dos_handles[hd]
                f.close()
                del self.dos_handles[hd]
                self.clear_cf()
        elif ah == 0x3f:
            hd = self.ql.reg.bx
            if hd not in self.dos_handles:
                self.ql.reg.ax = 0x6
                self.set_cf()
            else:
                f = self.dos_handles[hd]
                buffer = self.calculate_address(self.ql.reg.ds, self.ql.reg.dx)
                sz = self.ql.reg.cx
                rd = f.read(sz)
                self.ql.mem.write(buffer, rd)
                self.clear_cf()
                self.ql.reg.ax = len(rd)
        elif ah == 0x40:
            hd = self.ql.reg.bx
            if hd not in self.dos_handles:
                self.ql.reg.ax = 0x6
                self.set_cf()
            else:
                f = self.dos_handles[hd]
                buffer = self.calculate_address(self.ql.reg.ds, self.ql.reg.dx)
                sz = self.ql.reg.cx
                rd = self.ql.mem.read(buffer, sz)
                f.write(bytes(rd))
                self.clear_cf()
                self.ql.reg.ax = len(rd)
        elif ah == 0x41:
            fname = self.read_dos_string_from_ds_dx()
            real_path = PathUtils.convert_for_native_os(self.ql.rootfs, self.ql.cur_path, fname)
            try:
                os.remove(real_path)
                self.clear_cf()
            except OSError:
                self.ql.reg.ax = 0x5
                self.set_cf()
        elif ah == 0x43:
            self.ql.reg.cx = 0xFFFF
            self.clear_cf()
        else:
            raise NotImplementedError()

    def hook_syscall(self):
        def cb(ql, intno, user_data=None):
            # http://spike.scu.edu.au/~barry/interrupts.html
            # http://www2.ift.ulaval.ca/~marchand/ift17583/dosints.pdf
            ql.nprint(f"[!] INT={intno:x}, AH={ql.reg.ah:x}")
            if intno == 0x21:
                self.int21()
            elif intno == 0x10:
                self.int10()
            elif intno == 0x16:
                self.int16()
            elif intno == 0x13:
                self.int13()
            elif intno == 0x1a:
                self.int1a()
            else:
                raise NotImplementedError()
        self.ql.hook_intr(cb)

    def run(self):
        if self.ql.exit_point is not None:
            self.exit_point = self.ql.exit_point

        if  self.ql.entry_point is not None:
            self.ql.loader.elf_entry = self.ql.entry_point
        else:
            self.ql.entry_point = self.ql.loader.start_address
        if not self.ql.shellcoder:
            try:
                self.ql.emu_start(self.ql.entry_point, self.exit_point, self.ql.timeout, self.ql.count)
            except UcError:
                self.emu_error()
                raise

            if self.ql.internal_exception != None:
                raise self.ql.internal_exception 