#! /usr/bin/env python
# coding:gbk
import mp_img_sync
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR
from global_config import logger


class Scheduler:

    def __init__(self, inertval=5):
        self.scheduler = BlockingScheduler()
        self.inertval = inertval

    def start(self):
        sync = mp_img_sync.SyncImg2DingTalk(delete_pic=False)
        self.scheduler.add_job(sync.run, 'interval', id='mp_sync_job', seconds=self.inertval)
        self.scheduler.add_listener(self.my_listener, EVENT_JOB_ERROR)
        self.scheduler.start()

    def my_listener(self, event):
        if event.exception:
            logger.error('The job crashed :(')
            self.scheduler.shutdown(wait=False)


if __name__ == '__main__':
    sched = Scheduler(10)
    sched.start()
