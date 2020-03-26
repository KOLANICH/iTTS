import typing
from abc import ABC, abstractmethod

class IMagicsAutocompleter():
	__slots__ = ()
	def __init__(self, magicsDict):
		pass

	@abstractmethod
	def __getitem__(self, k):
		raise NotImplementedError()

	@abstractmethod
	def completeCommandName(self, prefix):
		raise NotImplementedError()

class DictMagicsAutocompleter(IMagicsAutocompleter):
	__slots__ = ("dic",)

	def __init__(self, magicsDict):
		self.dic = magicsDict

	def __getitem__(self, k):
		return self.dic[k]

	def completeCommandName(self, prefix):
		return [c for c in self.dic if c.startswith(prefix)]

ChosenMagicsCompleter = DictMagicsAutocompleter

try:
	import datrie

	class DaTrieMagicsAutocompleter(IMagicsAutocompleter):
		__slots__ = ("trie",)
		char_ranges = (("a", "z"), ("A", "Z"), ("0", "9"), ("_", "_"))

		def __init__(self, magicsDict):
			self.trie = datrie.Trie(ranges=self.__class__.char_ranges)
			for k, v in magicsDict.items():
				self.trie[k] = v

		def __getitem__(self, k):
			return self.trie[k]

		def completeCommandName(self, prefix):
			return [prefix + c for c in self.trie.suffixes(prefix)]

	ChosenMagicsCompleter = DaTrieMagicsAutocompleter
except ImportError:
	pass
