from utilities import Domain, Workflow, Activity, logger
import boto3, uuid, time, threading
from botocore.client import Config


botoConfig = Config(connect_timeout=70, read_timeout=90)
swf = boto3.client('swf', config=botoConfig)

# set up domain
MyDomain = Domain(swf=swf,
                  name='dev',
                  description='Test SWF domain',
                  workflowExecutionRetentionPeriodInDays='10')

# set up workflow
MyWorkflow = Workflow(swf=swf,
                      Domain=MyDomain,
                      name="Testing",
                      description="Test workflow",
                      version="1.0.0",
                      defaultExecutionStartToCloseTimeout="250",
                      defaultTaskStartToCloseTimeout="NONE",
                      defaultChildPolicy="TERMINATE",
                      defaultTaskList={"name": "tasks" })

# add activities
MyActivity1 = Activity(name="activity1",
                       version="1.0.0", # string
                       description="Activity #1",
                       defaultTaskStartToCloseTimeout="NONE",
                       defaultTaskList={"name": "tasks1" })
MyActivity2 = Activity(name="activity2",
                       version="1.0.0", # string
                       description="Activity #2",
                       defaultTaskStartToCloseTimeout="NONE",
                       defaultTaskList={"name": "tasks2" })
MyActivity3 = Activity(name="activity3",
                       version="1.0.0", # string
                       description="Activity #3",
                       defaultTaskStartToCloseTimeout="NONE",
                       defaultTaskList={"name": "tasks3" })

# register domain, workflow, activity
MyDomain.register_domain()
MyWorkflow.register_workflow_type()
MyWorkflow.register_activity_type(MyActivity1)
MyWorkflow.register_activity_type(MyActivity2)
MyWorkflow.register_activity_type(MyActivity3)



def generator():
    interval = 3;
    logger.info("Now Generating NEW Workflows every " + str(interval) + " seconds...")

    while True:
        time.sleep(interval)
        id = 'workflow-id-' + str(uuid.uuid4())
        response = swf.start_workflow_execution(
            domain=MyDomain.NAME,
            workflowId=id,
            workflowType={
                "name": MyWorkflow.NAME,
                "version": MyWorkflow.VERSION
            },
            taskList=MyWorkflow.DEFAULT_TASK_LIST,
            input=''
        )
        logger.info("Requested Workflow Execution with ID:  " + id + " and received RunId:" + response['runId'])


def decider():
    logger.info("Listening for Decision Tasks....")

    while True:
        newTask = swf.poll_for_decision_task(
            domain=MyDomain.NAME ,
            taskList=MyWorkflow.DEFAULT_TASK_LIST,
            identity='decider-' + str(uuid.uuid4()), # any identity you would like to provide, it's recorded in the history
            reverseOrder=False)

        if 'taskToken' not in newTask:

            logger.warning("Decision poll timeout, no new task found. Repolling..")

        elif 'events' in newTask:

            eventHistory = [evt for evt in newTask['events'] if not evt['eventType'].startswith('Decision')]
            lastEvent = eventHistory[-1]

            if lastEvent['eventType'] == 'WorkflowExecutionStarted':

                logger.info("Dispatching task to worker!\n" + newTask['taskToken'] + "\n" + str(newTask['workflowExecution']) + "\n" + str(newTask['workflowType']))
                activityId = 'activityid-' + str(uuid.uuid4());
                swf.respond_decision_task_completed(
                    taskToken=newTask['taskToken'],
                    decisions=[
                        {
                            'decisionType': 'ScheduleActivityTask',
                            'scheduleActivityTaskDecisionAttributes': {
                                'activityType':{
                                    'name': MyActivity1.NAME, # string
                                    'version': MyActivity1.VERSION # string
                                },
                                'activityId': activityId,
                                'input': '',
                                'scheduleToCloseTimeout': 'NONE',
                                'scheduleToStartTimeout': 'NONE',
                                'startToCloseTimeout': 'NONE',
                                'heartbeatTimeout': 'NONE',
                                'taskList': MyWorkflow.DEFAULT_TASK_LIST,
                            }
                        }
                    ]
                )

                logger.info("Task Dispatched!" + "\n" + newTask['taskToken'] + "\n" + activityId + '\n' + MyActivity1.NAME)

            elif lastEvent['eventType'] == 'ActivityTaskCompleted':
                swf.respond_decision_task_completed(
                    taskToken=newTask['taskToken'],
                    decisions=[
                        {
                            'decisionType': 'CompleteWorkflowExecution',
                            'completeWorkflowExecutionDecisionAttributes': {
                                'result': 'success'
                            }
                        }
                    ]
                )

                logger.info("Task Completed!"  + "\n" + str(newTask['taskToken']))

            elif lastEvent['eventType'] == 'WorkflowExecutionTimedOut':
                logger.error("Execution Time Out for \n" + str(newTask['taskToken']))

def worker():
    logger.info("Listening for Worker Tasks....")

    while True:
        task = swf.poll_for_activity_task(
            domain=MyDomain.NAME,# string
            taskList=MyWorkflow.DEFAULT_TASK_LIST, # TASKLIST is a string
            identity='worker-'+str(uuid.uuid4())) # identity is for our history

        if 'taskToken' not in task:
            logger.warning("Worker poll timeout, no new task found. Repolling..")
        else:
            logger.info("New Worker task arrived!\n" + str(task['activityId']) + "\n" + str(task['workflowExecution']) + "\n" + str(task['taskToken']))

            swf.respond_activity_task_completed(
                taskToken=task['taskToken'],
                result='success'
            )

            logger.info("Worker Task Complete!\n" + str(task['activityId']) + "\n" + str(task['workflowExecution']))


# set up threads for worker, decider, and generator
w = threading.Thread(target=worker)
d = threading.Thread(target=decider)
g = threading.Thread(target=generator)
w.start()
d.start()
g.start()
