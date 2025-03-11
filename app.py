import door_rev
import door_send
from multiprocessing import Process , Queue


def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


@Singleton
class DataService(object):
    def __init__(self):

        self.queue_door = Queue()

        self.p_rev = Process(
            target=door_rev.main,
            args=(self.queue_door,),
            name="doordata_rev_phm",
            daemon=True,
        )

        # network process
        self.p_send = Process(
            target=door_send.main,
            args=(self.queue_door,),
            name="doordata_send_phm",
            daemon=True,
        )

        self.procs = [
            self.p_rev,
            self.p_send
        ]

    def run(self):
        """start ocu data services"""

        try:
            for p in self.procs:
                p.start()
            for p in self.procs:
                p.join()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    data_service = DataService()
    data_service.run()
