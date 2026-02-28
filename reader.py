from typing import Callable, Optional, Tuple, Union

import pymem


class Reader:
    MODULE_BASE_OFFSET = 0x03C078D0
    ANHEN_OFFSETS = 0x530
    WANGZHENG_OFFSETS = 0x4BC
    QUANTITY_OFFSET = 0x39AA448

    def __init__(self, pid: Optional[int] = None, exe_module_name: str = ""):
        self.pid: Optional[int] = pid
        self.exe_module_name: str = exe_module_name.lower()
        self.pm: Optional[pymem.Pymem] = None
        self._cached_exe_base: Optional[int] = None
        self._cached_anhen_ptr: Optional[int] = None
        self._cached_wangzheng_ptr: Optional[int] = None
        self._cached_quantity_ptr: Optional[int] = None
        self.resetPID(pid)
    
    def resetPID(self, pid: Optional[int] = None) -> None:
        self.pid = pid
        self.pm = None
        self._clear_cache()
        if pid:
            try:
                self.pm = pymem.Pymem(pid)
            except Exception:
                self.pm = None

    def _clear_cache(self) -> None:
        self._cached_exe_base = None
        self._cached_anhen_ptr = None
        self._cached_wangzheng_ptr = None
        self._cached_quantity_ptr = None

    def _get_module_base(self) -> Optional[int]:
        if self._cached_exe_base:
            try:
                self.pm.read_bytes(self._cached_exe_base, 1)
                return self._cached_exe_base
            except Exception:
                self._cached_exe_base = None
        
        if not self.pm:
            return None
        
        try:
            for m in self.pm.list_modules():
                if self.exe_module_name in m.name.lower():
                    self._cached_exe_base = m.lpBaseOfDll
                    return self._cached_exe_base
            return None
        except Exception:
            return None
    
    def _read_memory(self, offset: int, use_pointer: bool = True) -> Tuple[Optional[int], int]:
        if not self.pm:
            return (None, -1)
        
        exe_base = self._get_module_base()
        if not exe_base:
            return (None, -1)
        
        try:
            if use_pointer:
                base_ptr = self.pm.read_longlong(exe_base + self.MODULE_BASE_OFFSET)
                if base_ptr == 0:
                    return (None, -1)
                target_ptr = base_ptr + offset
            else:
                target_ptr = exe_base + offset
            
            value = self.pm.read_longlong(target_ptr)
            return (target_ptr, value)
        except Exception:
            return (None, -1)
    
    def _read_pointer(self, offset: int) -> Tuple[Optional[int], int]:
        return self._read_memory(offset, use_pointer=True)
    
    def _read_direct(self, offset: int) -> Tuple[Optional[int], int]:
        return self._read_memory(offset, use_pointer=False)
    
    def get_anhen(self) -> int:
        ptr, value = self._read_pointer(self.ANHEN_OFFSETS)
        self._cached_anhen_ptr = ptr
        return value
    
    def get_wangzheng(self) -> int:
        ptr, value = self._read_pointer(self.WANGZHENG_OFFSETS)
        self._cached_wangzheng_ptr = ptr
        return value
    
    def get_quantity(self) -> int:
        ptr, value = self._read_direct(self.QUANTITY_OFFSET)
        self._cached_quantity_ptr = ptr
        return value
    
    def _set_value(self, value: Union[int, float], cached_ptr: Optional[int], 
                   get_method: Callable[[], int]) -> bool:
        if not isinstance(value, (int, float)):
            return False
        
        value = int(value)
        if value < 0:
            return False
        
        if not self.pm:
            return False
        
        if 'anhen' in get_method.__name__:
            cache_attr = '_cached_anhen_ptr'
        elif 'wangzheng' in get_method.__name__:
            cache_attr = '_cached_wangzheng_ptr'
        elif 'quantity' in get_method.__name__:
            cache_attr = '_cached_quantity_ptr'
        else:
            return False
            
        if not cached_ptr:
            cached_ptr = getattr(self, cache_attr)
            if not cached_ptr:
                get_method()
                cached_ptr = getattr(self, cache_attr)
        
        if cached_ptr:
            try:
                self.pm.read_bytes(cached_ptr, 1)
                self.pm.write_longlong(cached_ptr, value)
                return True
            except Exception:
                setattr(self, cache_attr, None)
                return False
        return False
    
    def set_anhen(self, value: Union[int, float]) -> bool:
        return self._set_value(value, self._cached_anhen_ptr, self.get_anhen)
    
    def set_wangzheng(self, value: Union[int, float]) -> bool:
        return self._set_value(value, self._cached_wangzheng_ptr, self.get_wangzheng)
    
    def close(self) -> None:
        if self.pm:
            try:
                self.pm.close_process()
            except Exception:
                pass