import inspect
from collections import defaultdict
import functools

from ipykernel.kernelbase import Kernel
import speechd
from .__version__ import __version__
from .MagicsAutoCompleter import ChosenMagicsCompleter


# Largery based on https://github.com/takluyver/bash_kernel/blob/68c922de28fb09bbb8cbe46b9717525e7afb619a/bash_kernel/kernel.py (licensed under BSD-3-Clause), but I have removed most of the non-trivial stuff and have written an own one

class CommandDescriptor:
	__slots__ = ("setter", "getter", "argsCount")

	def __init__(self, setter=None, getter=None, argsCount=0):
		self.setter = setter
		self.getter = getter
		self.argsCount = argsCount

	def __repr__(self):
		return self.__class__.__name__ + "(" + repr(self.setter) + ", " + repr(self.getter) + ", " + repr(self.argsCount) + ")"


class MagicCommand:
	__slots__ = ("name", "args")

	def __init__(self, name, args):
		self.name = name
		self.args = args

	def __repr__(self):
		return self.__class__.__name__ + "(" + repr(self.name) + ", " + repr(self.args) + ")"


class TTSKernel(Kernel):
	implementation = "tts_kernel"
	implementation_version = __version__

	@property
	def language_version(self):
		return 0

	_banner = None

	@property
	def banner(self):
		return repr({"socket": self.tts._conn._socket, "module": self.tts.get_output_module(), "lang": self.tts.get_language()})

	language_info = {
		"name": "",
		"version": __version__,
		"mimetype": "text/plain",
		"file_extension": ".txt"
	}

	def initializeMagics(self):
		possibleCommands = self.possibleCommands
		for c in dir(self.tts):
			if c[0] == "_":
				continue

			el = getattr(self.tts, c)
			if callable(el):
				s = inspect.signature(el)
				nonDefCount = len([(p.default is None) for p in s.parameters.values()])
				if len(c) > 3 and c[3] == "_":
					if c.startswith("set"):
						possibleCommands[c[4:]].setter = el
						continue
					elif c.startswith("get"):
						d = possibleCommands[c[4:]]
						d.getter = el
						d.argsCount = nonDefCount
						continue

				d = possibleCommands[c]
				d.setter = d.getter = el
				d.argsCount = nonDefCount
			else:
				d = possibleCommands[c]
				d.setter = functools.partial(setattr, self.tts, c)
				d.getter = functools.partial(getattr, self.tts)
				d.argsCount = 1

		possibleCommands["help"] = CommandDescriptor(None, lambda: " ".join(["%" + c for c in self.possibleCommands.keys()]), 0)

	def __init__(self, **kwargs):
		Kernel.__init__(self, **kwargs)

		self.tts = speechd.Speaker("jupyter_itts_kernel")
		self.possibleCommands = defaultdict(CommandDescriptor)
		self.initializeMagics()
		self.possibleCommands = ChosenMagicsCompleter(self.possibleCommands)

	def sendResult(self, res):
		return self.send_response(self.iopub_socket, "execute_result", {"execution_count": self.execution_count, "data": {"text/plain": res}, "metadata": {}})

	def sendError(self, ex):
		errMsg = {
			"execution_count": self.execution_count,
			"status": "error",
			"ename": str(ex),
			"evalue": str(ex),
			"traceback": []
		}
		self.send_response(self.iopub_socket, "error", errMsg)
		return {"status": "error", "execution_count": self.execution_count}

	def processMagicCommand(self, cmd):
		try:
			d = self.possibleCommands[cmd.name]
			if len(cmd.args) > d.argsCount:
				f = d.setter
			else:
				f = d.getter
			res = f(*cmd.args)
			if res is not None:
				self.sendResult(repr(res))
		except Exception as ex:
			return self.sendError(ex)

		return {"status": "ok", "execution_count": self.execution_count}

	def detect(self, code):
		code = code.strip()
		if len(code) >= 2:
			if code[0] == "%":
				if code[1] == "%":
					code = code[1:]
				else:
					args = code[1:].split(" ")
					return MagicCommand(args[0], args[1:])
		return code

	def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
		self.silent = silent
		code = code.splitlines()
		for l in code:
			l = self.detect(l)
			if not l:
				continue

			if isinstance(l, MagicCommand):
				self.processMagicCommand(l)
			else:
				interrupted = False
				try:
					res = self.tts.speak(l)
					if not self.silent:
						self.sendResult(repr(res))
				except KeyboardInterrupt:
					res = self.tts.cancel()
					if not self.silent:
						self.sendResult(repr(res))
				except Exception as ex:
					self.sendError(ex)

				if interrupted:
					return {"status": "abort", "execution_count": self.execution_count}

		return {"status": "ok", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}

	def do_shutdown(self, restart):
		self.tts.close()

	def do_complete(self, code, cursor_pos):
		eolPos = -1
		for i, c in enumerate(code[:cursor_pos]):
			if c == "\n":
				eolPos = i

		if cursor_pos >= 1:
			if code[0] == "%":
				startPos = eolPos + 2  # 1 for \n, 1 for %
				query = code[startPos:cursor_pos]
				matches = self.possibleCommands.completeCommandName(query)
				return {
					"status": "ok",
					"matches": matches,
					"cursor_start": startPos,
					"cursor_end": cursor_pos,
				}
