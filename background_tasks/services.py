import os
import signal

from background_tasks.models import BackgroundTask
from .task_list import back_tasks


class BackTaskService:

    def __init__(self):
        self.p_list = []
        self.started_tasks = []

    def __create_task_from_back_tasks(self, back_task):
        # p = back_task[2]()
        # p.start()
        # self.p_list.append((back_task[0], p))
        # if not BackgroundTask.objects.filter(local_id=back_task[0]).exists():
        #     BackgroundTask.objects.create(local_id=back_task[0], name=back_task[1], pid=p.pid, status=BackgroundTask.STATUS_RUNNING)
        # else:
        #     BackgroundTask.objects.filter(local_id=back_task[0]).update(status=BackgroundTask.STATUS_RUNNING)

        task = back_task[2]()
        task.start()
        self.started_tasks.append(task)

    def kill_and_create_new_back_tasks(self):

        self.kill_all_tasks_and_delete_from_db()

        for t in back_tasks:
            self.__create_task_from_back_tasks(t)

    def kill_all_tasks_and_delete_from_db(self):
        for t in self.p_list:
            t[2].set_event_and_join()
            # BackgroundTask.objects.filter(local_id=t[0]).delete()

        # for p in BackgroundTask.objects.all():
        #     try:
        #         os.kill(p.pid, signal.SIGTERM)
        #     except OSError:
        #         pass
        #     BackgroundTask.objects.get(pid=p.pid).delete()

    def kill_process_by_local_id(self, local_id: int):
        for t in self.p_list:
            if t[0] == local_id:
                t[1].set_event_and_join()
                self.p_list.remove(t)
                BackgroundTask.objects.filter(local_id=local_id).update(status=BackgroundTask.STATUS_KILL)
                break

    def start_process_by_local_id(self, local_id):
        back_task = None
        for t in back_tasks:
            if t[0] == local_id:
                back_task = t
                break
        if back_tasks is not None:
            self.__create_task_from_back_tasks(back_task)


background_task_service = BackTaskService()

