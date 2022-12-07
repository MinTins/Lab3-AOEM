# Flakey Roman K-23
# 18. 10h.24m
# F(a,b)=b-a/b+1.5/(a*b)


from ieee754 import IEEE754
from config import CoreSettings

import sys

TACT_WORK = True;


class CoProcessor:
	_HARACTERISE_BIT_LENGTH = CoreSettings.HARACTERISE_BIT_LENGTH;
	_MANTISE_BIT_LENGTH = CoreSettings.MANTISE_BIT_LENGTH;

	_RAM_SIZE = CoreSettings.RAM_SIZE;
	_STACK_SIZE = CoreSettings.STACK_SIZE;


	@staticmethod
	def to_hex(value):
		if isinstance(value, IEEE754):
			return value.__str_hex__()
		else:
			return hex(value)[2:].zfill(2)


	"""Stack functions"""

	def push_stack(self, value):
		if len(self._STACK) <= self._STACK_SIZE:

			if not isinstance(value, IEEE754):
				value = IEEE754(value)
			
			if len(self._STACK) < self._STACK_SIZE:
				self._STACK.append(value)
			else:
				self._STACK[-1] = (value)

			self._IX = len(self._STACK)-1


	def pop_stack(self):
		if len(self._STACK) > 0:
			val = self._STACK.pop()
			self._IX = len(self._STACK)-1
			return val 


	def duplication_stack(self):
		if 0 < len(self._STACK) < self._STACK_SIZE:
			self._STACK.append(self._STACK[-1])


	def reverse_stack(self):
		if len(self._STACK) > 1:
			self._STACK = self._STACK[:-2] + self._STACK[-1] + self._STACK[-2]
	
	""" Memory functions """

	def dump_in_memory(self, address):
		if len(self._STACK) > 0:
			elem = self._STACK.pop()
			self._RAM[address] = elem

	def load_from_memory(self, address):
		self.push_stack(self._RAM[address])

	def copy_memory(self, address1, address2):
		self._RAM[address2] = self._RAM[address1]



	def show(self):
		print("\n[ Command:", self._CMD,"]")
		print("Stack:", "\n".join(f"	{k}: {x}" for k,x in enumerate(self._STACK)), "	" + "[-] "*(self._STACK_SIZE-len(self._STACK)), sep="\n")
		mem_values = ".".join(map(self.to_hex, self._RAM.values()))
		print("Memory:", mem_values,
			".".join(str(k).zfill(2).center(len(mem_values[k])) for k in self._RAM.keys()), sep="\n	")

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

		elif cmd.startswith("pop stack"):
			self.pop_stack()
		
		elif cmd.startswith("dupl stack"):
			self.duplication_stack()
		
		elif cmd.startswith("rev stack"):
			self.reverse_stack()

		elif cmd.startswith("s_add stack"):
			if len(self._STACK) > 1:
				arg1 = self._STACK[-2]
				arg2 = self._STACK[-1]
				self.push_stack(arg1+arg2)

		elif cmd.startswith("s_sub stack"):
			if len(self._STACK) > 1:
				arg1 = self._STACK[-2]
				arg2 = self._STACK[-1]
				self.push_stack(arg1-arg2)

		elif cmd.startswith("s_mul stack"):
			if len(self._STACK) > 1:
				arg1 = self._STACK[-2]
				arg2 = self._STACK[-1]
				self.push_stack(arg1*arg2)

		elif cmd.startswith("s_tdiv stack"):
			if len(self._STACK) > 1:
				arg1 = self._STACK[-2]
				arg2 = self._STACK[-1]
				self.push_stack(arg1/arg2)
		
		elif cmd.startswith("F(stack)"): # Функція варіанту
			if len(self._STACK) > 1:
				arg1 = self._STACK[-2]
				arg2 = self._STACK[-1]
				self.push_stack(arg1.F(arg2))

		elif cmd.startswith("index "): # Робота з індексами
			arg1 = abs(int(cmd.split(" ", 1)[1]))
			arg1 %= self._STACK_SIZE
			self._IX = arg1

		elif cmd.startswith("mem_pop "): # Функції роботи з пам'яттю
			if len(self._STACK) > 0:
				arg1 = int(cmd.split(" ", 1)[1])
				self.dump_in_memory(arg1)

		elif cmd.startswith("mem_load "):
			arg1 = int(cmd.split(" ", 1)[1])
			self.load_from_memory(arg1)
		
		elif cmd.startswith("mem_copy "):
			addr1, addr2 = map(int, cmd.split(" ",1)[1].split(">", 1))
			self.copy_memory(addr1, addr2)

			

		self._TC += 1


	def cmd_procedure(self, command):
		if command.strip() == "" or command.strip().startswith("#"):
			return;

		self._prepare(command);
		#self.show();
		#self.tact()

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




def main():
	global TACT_WORK

	program_file = None;

	if len(sys.argv) > 1:
		if os.path.isfile(sys.argv[1]):
			program_file = sys.argv[1]
		
		if "-no-tact" in sys.argv:
			print("Tact stoping is off.")
			TACT_WORK = False

	if program_file is None:
		print("File not given. Used default program-file..")
		program_file = "program.txt"

	print("Load program file..")
	with open(program_file) as f:
		program_code = f.read().splitlines()
		f.close()

	print("Loaded program code:", *program_code, sep="\n ")

	print("Create simulation CoProcessor..")
	cp = CoProcessor()

	print("[ Info ]")
	IEEE754("0.0").show_info();

	print("Start program code on created simulation processor..")

	for line in program_code:
		cp.cmd_procedure(line)
	
	print("\nProgram finished.")



main()