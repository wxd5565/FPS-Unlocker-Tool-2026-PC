
# CheatEngine - External Cheat Engine for Gaming 2026
import ctypes
import time
import threading
import random
import math
from ctypes import wintypes

# ============= Memory Module =============
class CheatEngineMemory:
    """Handles low-level process memory operations."""
    PROCESS_VM_READ = 0x0010
    PROCESS_VM_WRITE = 0x0020
    PROCESS_VM_OPERATION = 0x0008

    def __init__(self, process_name="game.exe"):
        self.process_name = process_name
        self.pid = None
        self.handle = None
        self.base_address = 0

    def attach(self):
        """Attach to the target process."""
        try:
            self.pid = self._get_process_id()
            self.handle = ctypes.windll.kernel32.OpenProcess(
                CheatEngineMemory.PROCESS_VM_READ | CheatEngineMemory.PROCESS_VM_WRITE | CheatEngineMemory.PROCESS_VM_OPERATION,
                False, self.pid)
            if not self.handle:
                raise Exception("Failed to open process.")
            self.base_address = self._get_module_base()
            print(f"[+] Attached to {self.process_name} (PID {self.pid})")
        except Exception as e:
            print(f"[-] Error attaching: {e}")

    def _get_process_id(self):
        """Enumerate processes to find target."""
        # Simulated enumeration
        time.sleep(0.5)
        return random.randint(1000, 9999)

    def _get_module_base(self):
        """Return base address of the main module."""
        return random.randint(0x400000, 0x7fff0000) & 0xffff0000

    def read_int(self, address, offsets=None):
        """Read an integer from memory with optional offsets."""
        try:
            current = address
            if offsets:
                for offset in offsets[:-1]:
                    current = self.read_int(current) + offset
                current = self.read_int(current) + offsets[-1]
            buffer = ctypes.c_int()
            ctypes.windll.kernel32.ReadProcessMemory(self.handle, current, ctypes.byref(buffer), ctypes.sizeof(buffer), None)
            return buffer.value
        except:
            return 0

    def write_int(self, address, value, offsets=None):
        """Write an integer to memory."""
        try:
            current = address
            if offsets:
                for offset in offsets[:-1]:
                    current = self.read_int(current) + offset
                current = self.read_int(current) + offsets[-1]
            ctypes.windll.kernel32.WriteProcessMemory(self.handle, current, ctypes.byref(ctypes.c_int(value)), ctypes.sizeof(ctypes.c_int()), None)
            return True
        except:
            return False

    def read_float(self, address):
        buffer = ctypes.c_float()
        ctypes.windll.kernel32.ReadProcessMemory(self.handle, address, ctypes.byref(buffer), ctypes.sizeof(buffer), None)
        return buffer.value

    def close(self):
        if self.handle:
            ctypes.windll.kernel32.CloseHandle(self.handle)

# ============= Vector/Math Helpers =============
def calc_angle(local_pos, target_pos):
    delta = [target_pos[i] - local_pos[i] for i in range(3)]
    yaw = math.degrees(math.atan2(delta[1], delta[0]))
    hyp = math.sqrt(delta[0]**2 + delta[1]**2)
    pitch = -math.degrees(math.atan2(delta[2], hyp))
    return (pitch, yaw)

def normalize_angle(angle):
    while angle > 180: angle -= 360
    while angle < -180: angle += 360
    return angle

# ============= Aimbot =============
class CheatEngineAimbot:
    def __init__(self, mem: CheatEngineMemory):
        self.mem = mem
        self.fov = 2.0
        self.smooth = 1.5
        self.enabled = True
        self.ent_list = 0x12345678  # fake offset
        self.local_player = 0x110ABBCC

    def get_nearest_target(self):
        """Scan entity list and find closest enemy to crosshair."""
        local_pos = (self.mem.read_float(self.local_player),
                     self.mem.read_float(self.local_player+4),
                     self.mem.read_float(self.local_player+8))
        best_angle_diff = 999
        best_target = None
        view_angles = (self.mem.read_float(0xAABBCC), self.mem.read_float(0xAABBCC+4))
        for i in range(64):
            ent_base = self.mem.read_int(self.ent_list + i*0x10)
            if not ent_base: continue
            if ent_base == self.local_player: continue
            health = self.mem.read_int(ent_base + 0xFC)
            if health <= 0: continue
            target_pos = (self.mem.read_float(ent_base+0x34),
                          self.mem.read_float(ent_base+0x38),
                          self.mem.read_float(ent_base+0x3C))
            angle = calc_angle(local_pos, target_pos)
            diff = math.hypot(angle[0]-view_angles[0], angle[1]-view_angles[1])
            if diff < best_angle_diff and diff < self.fov:
                best_angle_diff = diff
                best_target = (ent_base, target_pos, angle)
        return best_target

    def aim_at(self, target_angle):
        if not self.enabled: return
        current = (self.mem.read_float(0xAABBCC), self.mem.read_float(0xAABBCC+4))
        new_yaw = current[0] + (target_angle[0] - current[0]) / self.smooth
        new_pitch = current[1] + (target_angle[1] - current[1]) / self.smooth
        self.mem.write_int(0xAABBCC, int(new_yaw*1000))
        self.mem.write_int(0xAABBCC+4, int(new_pitch*1000))

    def run_loop(self):
        while self.enabled:
            try:
                target = self.get_nearest_target()
                if target:
                    self.aim_at(target[2])
                time.sleep(0.001)
            except Exception as e:
                print(f"Aimbot error: {e}")
                time.sleep(0.1)

# ============= ESP / Wallhack =============
class CheatEngineESP:
    def __init__(self, mem: CheatEngineMemory):
        self.mem = mem
        self.enabled = True
        self.esp_colors = {"box": (0,255,0), "skeleton": (255,255,255)}
        # Overlay window handle placeholder
        self.overlay = None

    def create_overlay(self):
        """Initialize transparent overlay window."""
        # Simulated overlay creation
        print("[+] ESP overlay started")
        self.overlay = "HWND_OVERLAY"

    def draw_box(self, x, y, w, h):
        pass  # rendering engine call

    def draw_skeleton(self, bones):
        pass

    def run_loop(self):
        ent_list = 0x12345678
        while self.enabled:
            try:
                for i in range(64):
                    ent = self.mem.read_int(ent_list + i*0x10)
                    if not ent: continue
                    # Read position, draw box etc.
                    x = self.mem.read_float(ent+0x34)
                    y = self.mem.read_float(ent+0x38)
                    # Simulate drawing
                time.sleep(0.005)
            except:
                time.sleep(0.1)

# ============= Triggerbot =============
class CheatEngineTrigger:
    def __init__(self, mem: CheatEngineMemory):
        self.mem = mem
        self.enabled = True
        self.delay = 0.01  # seconds

    def is_crosshair_on_enemy(self):
        # Check crosshair ID
        cross_id = self.mem.read_int(0xCCAA0010)
        return cross_id > 0 and cross_id != 0xFFFF

    def shoot(self):
        # Simulate mouse click
        ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
        time.sleep(0.005)
        ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP

    def run_loop(self):
        while self.enabled:
            try:
                if self.is_crosshair_on_enemy():
                    self.shoot()
                    time.sleep(self.delay)
                else:
                    time.sleep(0.001)
            except:
                time.sleep(0.1)

# ============= Main Application =============
def main():
    print("Starting CheatEngine External Cheat...")
    mem = CheatEngineMemory("target_game.exe")
    mem.attach()

    aimbot = CheatEngineAimbot(mem)
