import asyncio
from datetime import timedelta
import logging
from typing import NoReturn
from saga import SagaBuilder, SagaError
from temporalio import activity, workflow
from temporalio.client import Client, WorkflowFailureError
from temporalio.common import RetryPolicy
from temporalio.worker import Worker

log = logging.getLogger("")
log.setLevel(logging.DEBUG)


USER_NUMBER = 0
val1 = -4
val2 = 20


class CompensationException(BaseException):
    pass


class ChangeValueException(BaseException):
    pass


def change_value_action1(val: int) -> NoReturn:
    global USER_NUMBER
    USER_NUMBER += val
    logging.debug(f"USER_NUMBER changed to {val}")
    # raise ChangeValueException(f"Change value Exception is raised while changing the {USER_NUMBER}")


def change_value_action2(val: int) -> NoReturn:
    global USER_NUMBER
    USER_NUMBER += val
    logging.debug(f"USER_NUMBER changed to {val}")
    raise ChangeValueException(f"Change value Exception is raised while changing the {USER_NUMBER}")


def compensation_action1(val) -> NoReturn:
    #global USER_NUMBER
    #USER_NUMBER -= val
    #logging.debug(f"Compensation_action1 executed, USER_NUMBER: {USER_NUMBER}")
    raise CompensationException("Compensation exception occured.")


def compensation_action2(val) -> NoReturn:
    global USER_NUMBER
    USER_NUMBER -= val
    logging.debug(f"Compensation_action2 executed, USER_NUMBER: {USER_NUMBER}")
    # raise CompensationException("Compensation exception occured.")


def cleanup_action() -> None:
    global USER_NUMBER
    USER_NUMBER = 0
    logging.debug("Resetting USER_NUMBER to initial value.")


@activity.defn
async def saga_activity() -> None:
    try:
        SagaBuilder \
            .create() \
            .action(lambda: change_value_action1(val1), lambda: compensation_action1(val1)) \
            .action(lambda: change_value_action2(val2), lambda: compensation_action2(val2)) \
            .build() \
            .execute()
    except SagaError as error:
        logging.debug(error)
        if error.compensations:
            cleanup_action()


@workflow.defn
class ChangeValueWorkflow:
    @workflow.run
    async def run(self) -> None:
        await workflow.execute_activity(
            saga_activity,
            start_to_close_timeout=timedelta(seconds=10),
            # We'll only retry once
            retry_policy=RetryPolicy(maximum_attempts=1),
        )


async def main():
    # Start client
    client = await Client.connect("localhost:7233")

    # Run a worker for the workflow
    async with Worker(
        client,
        task_queue="hello-rollback-task-queue",
        workflows=[ChangeValueWorkflow],
        activities=[saga_activity],
    ):

        # While the worker is running, use the client to start the workflow.
        # Note, in many production setups, the client would be in a completely
        # separate process from the worker.
        try:
            await client.execute_workflow(
                ChangeValueWorkflow.run,
                id="hello-change-value-workflow-id",
                task_queue="hello-rollback-task-queue",
            )
            logging.debug(f"USER_NUMBER: {USER_NUMBER}")

        except WorkflowFailureError as err:
            logging.exception(err)


if __name__ == "__main__":
    asyncio.run(main())
