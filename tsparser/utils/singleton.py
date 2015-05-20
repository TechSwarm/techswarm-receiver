from threading import Lock


class Singleton(type):
    _instances = {}
    _lock = Lock()

    def __call__(cls, *args, **kwargs):
        try:
            cls._lock.acquire()
            if cls not in cls._instances:
                cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            cls._lock.release()
            return cls._instances[cls]
        except:
            if cls._lock.locked():
                cls._lock.release()
            raise
