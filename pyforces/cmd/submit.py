from argparse import Namespace
import json
import os

from countdown.countdown import time
from websocket import WebSocketApp
from pyforces.client import Client
from pyforces.config import Config
from pyforces.utils import get_current_contest_type_id_problem_id, get_current_cpp_file
from logging import getLogger

logger = getLogger(__name__)


def do_submit(cfg: Config, cln: Client, args: Namespace):
    """ (Non-interactive) submit.
    Normal C++ users don't need to pass any arguments. Will use directory's name + ".cpp"
    Other languages users need to pass both --file and --program-type-id.

    For further customization, use --url and --problem-id
    """
    if args.file:
        source_file = args.file
    else:
        source_file = get_current_cpp_file()
        if not source_file:
            print(f"Please submit with  -f <file>")
            return

    if args.program_type_id:
        program_type_id = args.program_type_id
    else:
        program_type_id = {
            'cpp17': 54,
            'cpp20': 89,
            'cpp23': 91,
        }[cfg.submit_cpp_std]

    contest_type, contest_id, problem_id = get_current_contest_type_id_problem_id()
    submit_time = time.time()
    sub_info = cln.submit(
        url=args.url or f"{cfg.host}/{contest_type}/{contest_id}/submit",
        problem_id=args.problem_id or problem_id,
        program_type_id=program_type_id,
        source_file=source_file,
        track=args.track,
        strip_comment=args.strip_comment,
    )

    if args.track:
        if sub_info is None:
            print("Failed to fetch submission info")
            return
        sub_id, cc, pc = sub_info
        text = f"Watching submission {sub_id}"
        print(text)
        text += '\n    {status_render}'
        sub_status = {
            'test_id': 0,
            'status': '',
        }
        if args.poll is None:  # use websocket
            url = 'wss' if cfg.host.startswith('https') else 'ws'
            url += '://pubsub.' + cfg.host.split('://', 1)[1]
            url += f"/ws/s_{pc}/s_{cc}"
            url += f"?_={int(submit_time*1000)}&tag=&time=&eventid="

            def on_message(ws: WebSocketApp, message):
                try:
                    logger.info("Received websocket %s", message)
                    data = json.loads(json.loads(message)['text'])['d']
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error("ws decode error", exc_info=e)
                if data[1] != sub_id or data[2] != contest_id:
                    return
                sub_status['test_id'] = max(sub_status['test_id'], data[8])
                sub_status['status'] = data[6]
                status_render = sub_status['status']
                test_id = sub_status['test_id']
                if test_id:
                    status_render += f" {test_id}"
                os.system('clear' if os.name == 'posix' else 'cls')
                print(text.format(status_render=status_render))
                if not status_render.startswith(('TESTING', 'SUBMITTED')):
                    # the list is in the drop-down menu of status filter
                    # maybe SUBMITTED is not required?
                    ws.close()

            def on_error(ws, error):
                logger.error("Error from websocket %s", error)

            def on_close(ws, close_status_code, close_msg):
                logger.info("Disconnected from websocket")

            def on_open(ws):
                logger.info("Connected to the server!")
                # Subscribe to channels (adjust based on server requirements)
                # ws.send(json.dumps({"subscribe": "global-channel"}))
                # ws.send(json.dumps({"subscribe": "user-channel"}))
                ws.send(json.dumps({"subscribe": "contest-channel"}))
                # ws.send(json.dumps({"subscribe": "participant-channel"}))
                # ws.send(json.dumps({"subscribe": "talk-channel"}))

            ws = WebSocketApp(
                url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever()

        else:  # use polling
            url = f"{cfg.host}/contest/{contest_id}/submission/{sub_id}"
            while True:
                status_render = cln.parse_status(url)
                os.system('clear' if os.name == 'posix' else 'cls')
                print(text.format(status_render=status_render))
                if not status_render.startswith(["Running", "Pending"]):
                    break
                time.sleep(args.poll)

