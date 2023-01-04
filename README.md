# Temporal Python SDK Samples

This is the set of Python samples for the [Python SDK](https://github.com/temporalio/sdk-python).

**UNDER DEVELOPMENT**

The Python SDK is under development. There are no compatibility guarantees nor proper documentation pages at this time.

## How to run Temporalio ?

Install docker 

* [Docker installation](https://docs.docker.com/engine/install/)

Install docker-compose 

* [Docker compose installation](https://docs.docker.com/compose/install/)


Clone and Run Temporalio

```
git clone https://github.com/temporalio/docker-compose.git
cd docker-compose
docker compose up
```

You should have Temporal Cluster running at http://127.0.0.1:7233 and The Temporal Web UI at http://127.0.0.1:8080.

## Install Dependencies

```
pip install temporalio poetry
```

## Get the Samples

```
pip install temporalio poetry
git clone https://github.com/temporalio/samples-python.git
cd  samples-python
```

## Usage of Samples

Prerequisites:

* Python >= 3.7
* [Poetry](https://python-poetry.org)
* [Local Temporal server running](https://docs.temporal.io/clusters/quick-install/)

With this repository cloned, run the following at the root of the directory:

    poetry install

That loads all required dependencies. Then to run a sample, usually you just run it in Python. For example:

    poetry run python hello/hello_activity.py

Some examples require extra dependencies. See each sample's directory for specific instructions.

## Samples

* [hello](hello) - All of the basic features.
  <!-- Keep this list in alphabetical order and in sync on hello/README.md and root README.md -->
  * [hello_activity](hello/hello_activity.py) - Execute an activity from a workflow.
  * [hello_rollback](hello/hello_activity.py) - Execute an activity and run another compensation activity if it fails
  * [hello_rollback_with_saga](hello/hello_activity.py) - Execute an activity which includes several actions with their compensations using Saga
  * [hello_activity_choice](hello/hello_activity_choice.py) - Execute certain activities inside a workflow based on
    dynamic input.
  * [hello_activity_multiprocess](hello/hello_activity_multiprocess.py) - Execute a synchronous activity on a process
    pool.
  * [hello_activity_retry](hello/hello_activity_retry.py) - Demonstrate activity retry by failing until a certain number
    of attempts.
  * [hello_activity_threaded](hello/hello_activity_threaded.py) - Execute a synchronous activity on a thread pool.
  * [hello_async_activity_completion](hello/hello_async_activity_completion.py) - Complete an activity outside of the
    function that was called.
  * [hello_cancellation](hello/hello_cancellation.py) - Manually react to cancellation inside workflows and activities.
  * [hello_child_workflow](hello/hello_child_workflow.py) - Execute a child workflow from a workflow.
  * [hello_continue_as_new](hello/hello_continue_as_new.py) - Use continue as new to restart a workflow.
  * [hello_cron](hello/hello_cron.py) - Execute a workflow once a minute.
  * [hello_exception](hello/hello_exception.py) - Execute an activity that raises an error out of the workflow and out
    of the program.
  * [hello_local_activity](hello/hello_local_activity.py) - Execute a local activity from a workflow.
  * [hello_mtls](hello/hello_mtls.py) - Accept URL, namespace, and certificate info as CLI args and use mTLS for
    connecting to server.
  * [hello_parallel_activity](hello/hello_parallel_activity.py) - Execute multiple activities at once.
  * [hello_query](hello/hello_query.py) - Invoke queries on a workflow.
  * [hello_search_attributes](hello/hello_search_attributes.py) - Start workflow with search attributes then change
    while running.
  * [hello_signal](hello/hello_signal.py) - Send signals to a workflow.
<!-- Keep this list in alphabetical order -->
* [activity_worker](activity_worker) - Use Python activities from a workflow in another language.
* [custom_converter](custom_converter) - Use a custom payload converter to handle custom types.
* [custom_decorator](custom_decorator) - Custom decorator to auto-heartbeat a long-running activity.
* [encryption](encryption) - Apply end-to-end encryption for all input/output.
* [open_telemetry](open_telemetry) - Trace workflows with OpenTelemetry.
* [sentry](sentry) - Report errors to Sentry.

## Test

Running the tests requires `poe` to be installed.

    python -m pip install poethepoet

Once you have `poe` installed you can run:

    poe test

## Rollback with Temporalio

Execute the compensation actions by using only Temporal

`python hello_rollback.py`

```
Completing activity as failed ({'activity_id': '1', 'activity_type': 'change_value_activity', 'attempt': 1, 'namespace': 'default', 'task_queue': 'hello-rollback-task-queue', 'workflow_id': 'hello-change-value-workflow-id', 'workflow_run_id': '1073840f-e457-4716-ad41-91cbb38c2048', 'workflow_type': 'ChangeValueWorkflow'})
Traceback (most recent call last):
  File "/home/gatici/OSM/temporal/samples-python/venv/lib/python3.8/site-packages/temporalio/worker/_activity.py", line 402, in _run_activity
    result = await impl.execute_activity(input)
  File "/home/gatici/OSM/temporal/samples-python/venv/lib/python3.8/site-packages/temporalio/worker/_activity.py", line 640, in execute_activity
    return await input.fn(*input.args)
  File "hello_rollback.py", line 30, in change_value_activity
    raise ChangeValueException(f"Change value Exception is raised while changing the {USER_NUMBER}")
ChangeValueException: Change value Exception is raised while changing the 9
DEBUG:root:Resetting USER_NUMBER to initial value.
DEBUG:temporalio.worker._activity:Completing activity with completion: task_token: "\n$a58613cf-f986-4148-8747-fc4a2fdf14b6\022 hello-rollback-workflow-child-id\032$c09642b4-9c49-4644-bb98-b47578d8f1c2 \005(\0012\0011B\025compensation_activityJ\t\010\004\020\325\263\200\002\030\001"
result {
  completed {
    result {
      metadata {
        key: "encoding"
        value: "binary/null"
      }
    }
  }
}

DEBUG:root:USER_NUMBER: 0
INFO:temporalio.worker._worker:Beginning worker shutdown, will wait 0:00:00 before cancelling activities
```


Execute the compensation actions by using Saga on Temporal
`python hello_rollback_with_saga.py`

```
DEBUG:root:USER_NUMBER changed to -4
DEBUG:root:USER_NUMBER changed to 20
DEBUG:root:Compensation_action2 executed, USER_NUMBER: -4
DEBUG:root:(ChangeValueException('Change value Exception is raised while changing the 16'), [CompensationException('Compensation exception occured.')])
DEBUG:root:Resetting USER_NUMBER to initial value.
DEBUG:temporalio.worker._activity:Completing activity with completion: task_token: "\n$a58613cf-f986-4148-8747-fc4a2fdf14b6\022\036hello-change-value-workflow-id\032$de605580-ab06-4543-a39b-6ba3f0451e06 \005(\0012\0011B\rsaga_activityJ\t\010\004\020\207\264\200\002\030\001"
result {
  completed {
    result {
      metadata {
        key: "encoding"
        value: "binary/null"
      }
    }
  }
}

DEBUG:root:USER_NUMBER: 0
INFO:temporalio.worker._worker:Beginning worker shutdown, will wait 0:00:00 before cancelling activities
```
