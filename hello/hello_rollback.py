import asyncio
from datetime import timedelta
import logging
from typing import NoReturn
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker
from temporalio.exceptions import ActivityError

log = logging.getLogger("")
log.setLevel(logging.DEBUG)

USER_NUMBER = 0
val = 9


class CompensationException(RuntimeError):
    pass


class ChangeValueException(RuntimeError):
    pass


@activity.defn
async def change_value_activity() -> NoReturn:
    global USER_NUMBER
    USER_NUMBER += val
    raise ChangeValueException(f"Change value Exception is raised while changing the {USER_NUMBER}")


@activity.defn
async def compensation_activity() -> NoReturn:
    try:
        compensation_action()
    except CompensationException:
        cleanup_action()


def compensation_action() -> None:
    # global USER_NUMBER
    # USER_NUMBER -= val
    # logging.debug(f"Compensation is done, USER_NUMBER: {USER_NUMBER}")
    raise CompensationException("Compensation exception occured.")


def cleanup_action() -> None:
    global USER_NUMBER
    USER_NUMBER = 0
    logging.debug("Resetting USER_NUMBER to initial value.")


@workflow.defn
class ChangeValueWorkflow:
    @workflow.run
    async def run(self) -> None:
        try:
            await workflow.execute_activity(
                change_value_activity,
                start_to_close_timeout=timedelta(seconds=10),
                # We'll only retry once
                retry_policy=RetryPolicy(maximum_attempts=1),
            )
        except ActivityError:
            await workflow.execute_child_workflow(
                RollbackWorkflow.run,
                id="hello-rollback-workflow-child-id",
            )


@workflow.defn
class RollbackWorkflow:
    @workflow.run
    async def run(self) -> None:
        # Execute the forever running activity, and do a cleanup activity when
        # it is complete (on error or cancel)
        await workflow.execute_activity(
            compensation_activity,
            start_to_close_timeout=timedelta(seconds=10),
            # We'll only retry once
            retry_policy=RetryPolicy(maximum_attempts=2),
        )


async def main():
    # Start client
    client = await Client.connect("localhost:7233")

    # Run a worker for the workflow
    async with Worker(
        client,
        task_queue="hello-rollback-task-queue",
        workflows=[ChangeValueWorkflow, RollbackWorkflow],
        activities=[change_value_activity, compensation_activity],
    ):

        # While the worker is running, use the client to start the workflow.
        # Note, in many production setups, the client would be in a completely
        # separate process from the worker.

        await client.execute_workflow(
            ChangeValueWorkflow.run,
            id="hello-change-value-workflow-id",
            task_queue="hello-rollback-task-queue",
        )
        logging.debug(f"USER_NUMBER: {USER_NUMBER}")


if __name__ == "__main__":
    asyncio.run(main())
