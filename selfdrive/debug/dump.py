#!/usr/bin/env python3
import sys
import argparse
import json
import codecs

from hexdump import hexdump
from cereal import log
from cereal.services import SERVICE_LIST
from openpilot.tools.lib.logreader import raw_live_logreader


codecs.register_error("strict", codecs.backslashreplace_errors)

if __name__ == "__main__":

  parser = argparse.ArgumentParser(description='Dump communication sockets. See cereal/services.py for a complete list of available sockets.')
  parser.add_argument('--pipe', action='store_true')
  parser.add_argument('--raw', action='store_true')
  parser.add_argument('--json', action='store_true')
  parser.add_argument('--dump-json', action='store_true')
  parser.add_argument('--no-print', action='store_true')
  parser.add_argument('--addr', default='127.0.0.1')
  parser.add_argument('--values', help='values to monitor (instead of entire event)')
  parser.add_argument("socket", type=str, nargs='*', default=list(SERVICE_LIST.keys()), help="socket names to dump. defaults to all services defined in cereal")
  args = parser.parse_args()

  lr = raw_live_logreader(args.socket, args.addr)

  values = None
  if args.values:
    values = [s.strip().split(".") for s in args.values.split(",")]

  for msg in lr:
    with log.Event.from_bytes(msg) as evt:
      if not args.no_print:
        if args.pipe:
          sys.stdout.write(str(msg))
          sys.stdout.flush()
        elif args.raw:
          hexdump(msg)
        elif args.json:
          print(json.loads(msg))
        elif args.dump_json:
          print(json.dumps(evt.to_dict()))
        elif values:
          print(f"logMonotime = {evt.logMonoTime}")
          for value in values:
            if hasattr(evt, value[0]):
              item = evt
              for key in value:
                item = getattr(item, key)
              print(f"{'.'.join(value)} = {item}")
          print("")
        else:
          try:
            print(evt)
          except UnicodeDecodeError:
            w = evt.which()
            s = f"( logMonoTime {evt.logMonoTime} \n  {w} = "
            s += str(evt.__getattr__(w))
            s += f"\n  valid = {evt.valid} )"
            print(s)
