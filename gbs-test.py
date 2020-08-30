import sys
import textwrap
import os
import os.path

import adhesive
from adhesive.workspace import docker


class Context:
    redis_id: str
    test_image_id: str


@adhesive.task("Start Redis Container")
def start_redis_container(context: adhesive.Token[Context]) -> None:
    context.data.redis_id = context.workspace.run_output("docker run -d redis").strip()


@adhesive.task("Run Integration Tests")
def run_integration_tests(context: adhesive.Token[Context]) -> None:
    redis_id = context.data.redis_id
    cwd = os.path.abspath(os.path.curdir)

    command = textwrap.dedent(
        f"""\
        docker run -t \\
                --rm \\
                --link {redis_id}:redis \\
                -v {cwd}:{cwd} \\
                -w {cwd} \\
                -e REDINO_HOST=redis \\
                {context.data.test_image_id} \\
                python -m unittest
        """
    )

    print(command)
    context.workspace.run(command)


@adhesive.task("Shutdown Redis Container")
def shutdown_redis_container(context: adhesive.Token) -> None:
    context.workspace.run(
        f"""
        docker rm -f {context.data.redis_id}
    """
    )


adhesive.bpmn_build(
    "gbs-test.bpmn",
    initial_data={
        "test_image_id": sys.argv[1],
    },
)
