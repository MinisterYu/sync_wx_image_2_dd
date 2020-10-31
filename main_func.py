# -*- coding: gb2312 -*-
# ! /usr/bin/env python
import mp_img_sync
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR
from global_config import logger


class Scheduler:

    # 间隔时间不宜设置太短，否则任务会存在跳过情况：http://www.debug5.com/detail/474/
    def __init__(self, inertval=30):
        self.scheduler = BlockingScheduler()
        self.inertval = inertval

    def start(self):
        sync = mp_img_sync.SyncImg2DingTalk(delete_pic=True)
        self.scheduler.add_job(sync.run, 'interval', id='mp_sync_job', seconds=self.inertval)
        self.scheduler.add_listener(self.my_listener, EVENT_JOB_ERROR)
        self.scheduler.start()

    def my_listener(self, event):
        if event.exception:
            logger.error('The job crashed :(')
            self.scheduler.shutdown(wait=False)


if __name__ == '__main__':
    sched = Scheduler()
    sched.start()
