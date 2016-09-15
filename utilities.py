from botocore.exceptions import ClientError
import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')


class Domain:
    def __init__(self, **kwargs):
        self.SWF = kwargs['swf']
        self.NAME = kwargs['name']
        self.DESCRIPTION = kwargs['description']
        self.RETENTION_PERIOD_IN_DAYS = kwargs['workflowExecutionRetentionPeriodInDays']

    def register_domain(self):
        try:
            self.SWF.register_domain(
                name=self.NAME,
                description=self.DESCRIPTION,
                workflowExecutionRetentionPeriodInDays=self.RETENTION_PERIOD_IN_DAYS # keep history for this long
            )
            logger.info("Domain registered: " + self.NAME)
        except ClientError as e:
            logger.warning("Domain already registered: " + self.NAME)

class Workflow:
    def __init__(self, **kwargs):
        self.SWF = kwargs['swf']
        self.NAME = kwargs['name']
        self.DESCRIPTION = kwargs['description']
        self.VERSION = kwargs['version']
        self.DEFAULT_EXECUTION_START_TO_CLOSE_TIMEOUT = kwargs['defaultExecutionStartToCloseTimeout']
        self.DEFAULT_TASK_START_TO_CLOSE_TIMEOUT = kwargs['defaultTaskStartToCloseTimeout']
        self.DEFAULT_CHILD_POLICY = kwargs['defaultChildPolicy']
        self.DEFAULT_TASK_LIST = kwargs['defaultTaskList']
        self.Domain = kwargs['Domain']

    def register_workflow_type(self):
        try:
            self.SWF.register_workflow_type(
                domain=self.Domain.NAME, # string
                name=self.NAME, # string
                version=self.VERSION, # string
                description=self.DESCRIPTION,
                defaultExecutionStartToCloseTimeout=self.DEFAULT_EXECUTION_START_TO_CLOSE_TIMEOUT,
                defaultTaskStartToCloseTimeout=self.DEFAULT_TASK_START_TO_CLOSE_TIMEOUT,
                defaultChildPolicy=self.DEFAULT_CHILD_POLICY,
                defaultTaskList=self.DEFAULT_TASK_LIST
            )
            logger.info("Workflow registered: " + self.NAME)
        except ClientError as e:
            logger.warning("Workflow already registered: " + self.NAME)

    def register_activity_type(self, Activity):
        try:
            self.SWF.register_activity_type(
                domain=self.Domain.NAME,
                name=Activity.NAME,
                version=Activity.VERSION, # string
                description=Activity.DESCRIPTION,
                defaultTaskStartToCloseTimeout=Activity.DEFAULT_TASK_START_TO_CLOSE_TIMEOUT,
                defaultTaskList=Activity.DEFAULT_TASK_LIST
            )
            logger.info("Activity registered: " + Activity.NAME)
        except ClientError as e:
            logger.warning("Activity already registered: " + Activity.NAME)


class Activity:
    def __init__(self, **kwargs):
        self.NAME = kwargs['name']
        self.DESCRIPTION = kwargs['description']
        self.VERSION = kwargs['version']
        self.DEFAULT_TASK_START_TO_CLOSE_TIMEOUT = kwargs['defaultTaskStartToCloseTimeout']
        self.DEFAULT_TASK_LIST = kwargs['defaultTaskList']