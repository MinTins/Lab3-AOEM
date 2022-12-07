# Flakey Roman K-23
# 18. 10h.24m
# F(a,b)=b-a/b+1.5/(a*b)


from ieee754 import IEEE754
from config import CoreSettings

TACT_WORK = False;


class CoProcessor:
	_HARACTERISE_BIT_LENGTH = CoreSettings.HARACTERISE_BIT_LENGTH;
	_MANTISE_BIT_LENGTH = CoreSettings.MANTISE_BIT_LENGTH;

	_RAM_SIZE = CoreSettings.RAM_SIZE;
	_STACK_SIZE = CoreSettings.STACK_SIZE;


	@staticmethod
	def to_hex(value):
		return hex(value)[2:].zfill(2)


	def push_stack(self, value):
		if len(self._STACK) < self._STACK_SIZE:
			ieee754_val = IEEE754(value)
			self._STACK.append(ieee754_val)

	def pop_stack(self):
		if len(self._STACK) > 0:
			self._STACK.pop()

	def pop_stack_in_memory(self, address):
		if len(self._STACK) > 0:
			self._RAM[address] = self._STACK.pop()


	def show(self):
		print("\nCommand:", self._CMD)
		print("\nStack:", "\n".join(f"	{k}: {x}" for k,x in enumerate(self._STACK)), "	" + "[-] "*(self._STACK_SIZE-len(self._STACK)), sep="\n")
		print("Memory:", 
			".".join(map(self.to_hex, self._RAM.values())),
			".".join(str(k).zfill(2) for k in self._RAM.keys()), sep="\n	")

		print("PS:", str(self._PS).ljust(10),"IX:", self._IX)
		print("PC:", str(self._PC).ljust(10),"TC:", self._TC)
	

	def tact(self):
		if TACT_WORK:
			input("Press Enter to next tact...")


	def _prepare(self, cmd):
		self._CMD = cmd;
		self._Ins = [];
		self._PC += 1;
		self._TC = 1;


	def _executer(self):
		cmd = self._CMD.strip()
		
		if cmd.startswith("push "):
			arg1 = cmd.split(" ", 1)[1]
			self.push_stack(arg1)

		self._TC += 1


	def cmd_procedure(self, command):
		if command.strip() == "" or command.strip().startswith("#"):
			return;

		self._prepare(command);
		self.show();
		self.tact()

		self._executer();
		self.show();
		self.tact()



	def __init__(self):
		self._RAM_BIT_LENGTH = self._STACK_BIT_LENGTH = self._HARACTERISE_BIT_LENGTH + self._MANTISE_BIT_LENGTH + 2;
		self._STACK = []
		self._RAM = {k:0 for k in range(self._RAM_SIZE)}

		self._CMD = ""
		self._IX = 0;
		self._PS = 0;
		self._PC = 0;
		self._TC = 0;


a = CoProcessor()
a.show()
a.cmd_procedure("push 12.2e-2")

