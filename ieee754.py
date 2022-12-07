from config import CoreSettings

import re


class IEEE754:
	_HARACTERISE_BIT_LENGTH = CoreSettings.HARACTERISE_BIT_LENGTH;
	_MANTISE_BIT_LENGTH = CoreSettings.MANTISE_BIT_LENGTH;


	def _set_exp(self, arr, exp):
		exp += self._HARACTERISE_SHIFT
		pos = self._HARACTERISE_BIT_LENGTH
		while exp:
			arr[pos] = exp % 2
			pos -= 1
			exp = exp // 2


	def _is_zero(self, x):
		_, e, m = self._ieee754_cutter(x)

		if m != 0:
			return False

		if e != self._MINIMUM_HARACTERISE:
			return False

		return True


	def _is_infinity(self, x):
		_, e, m = self._ieee754_cutter(x)

		if m != 0:
			return False

		if e != self._MAXIMUM_HARACTERISE:
			return False

		return True


	def _is_nan(self, x):
		if self._is_infinity(x):
			return False

		e = self._ieee754_cutter(x)[1]
		return e == self._MAXIMUM_HARACTERISE


	def _is_denormalized(self, x):
		if self._is_zero(x):
			return False

		e = self._ieee754_cutter(x)[1]
		return e == self._MINIMUM_HARACTERISE


	def ieee754_to_float(self, x):
		S, E, M = self._ieee754_cutter(x)
		if self._is_denormalized(x):
			return ((-1) ** S) * (2 ** E) * (M / (2 ** self._MANTISE_BIT_LENGTH))
		else:
			return ((-1) ** S) * (2 ** E) * (1 + M / (2 ** self._MANTISE_BIT_LENGTH))


	def float_to_ieee754(self, x):
		return self.str_to_ieee754(f'{x:.15f}')


	def _ieee754_cutter(self, x):
		s = x[0]

		e = 0
		for i in range(1, self._HARACTERISE_BIT_LENGTH + 1):
			e *= 2
			e += x[i]

		e -= self._HARACTERISE_SHIFT

		m = 0
		for i in range(self._HARACTERISE_BIT_LENGTH + 1, self._SUMMARY_BIT_LENGTH):
			m *= 2
			m += x[i]

		return s, e, m


	def ieee754_to_str(self, x=None):

		if isinstance(x, IEEE754):
			x = [x.sign, *x.haracterise, *x.mantise]

		result = []
		result.append(str(x[0]))  # sign
		result.append(self.comb_str(x[1:self._HARACTERISE_BIT_LENGTH + 1]))  # exponenta

		result.append(self.comb_str(x[self._HARACTERISE_BIT_LENGTH + 1:]))  # mantissa
		result.append("[-->]")

		mantiss_forgotten_bit = ''

		if self._is_zero(x):
			mantiss_forgotten_bit = '0'
			if x[0] == 1:
				result.append('-0.0')
			else:
				result.append('+0.0')
		elif self._is_infinity(x):
			mantiss_forgotten_bit = '1'
			if x[0] == 1:
				result.append('-∞')
			else:
				result.append('+∞')
		elif self._is_nan(x):
			mantiss_forgotten_bit = '0'
			result.append('NaN')
		else:
			if self._is_denormalized(x):
				mantiss_forgotten_bit = '0'
			else:
				mantiss_forgotten_bit = '1'
			result.append(f'{self.ieee754_to_float(x):.25f}')

		result.insert(2, mantiss_forgotten_bit)
		return ' '.join(result)


	def str_to_ieee754(self, a):
		result = [0] * self._SUMMARY_BIT_LENGTH
		sign = 0

		m = re.fullmatch(r"\s*(\+?|-)(\d+)(?:[,.](\d+)([eE]((?:\+?|-)\d+))?)?\s*", a)

		if m[1] == "-":
			sign = 1		
		
		val = f"{m[2]}.{m[3] if m[3] else ''}"

		exp = 0
		if m[4]:
			exp = int(m[5])

		if exp >= 0:
			for x in range(exp):
				dot_ind = val.find(".")
				if dot_ind==len(val)-2:
					val+="0"
				val = val[:dot_ind]+val[dot_ind+1]+"."+val[dot_ind+2:]

		else:
			for x in range(-exp):
				dot_ind = val.find(".")
				if dot_ind-1==0:
					val="0"+val
					dot_ind+=1

				val = val[:dot_ind-1]+"."+val[dot_ind-1]+val[dot_ind+1:]

		if '.' in val:
			a1, a2 = val.split('.')
		else:
			a1, a2 = a, '0'

		_divider = 10 ** len(a2)
		a1, a2 = int(a1), int(a2)

		_before = []
		while a1:
			_before.insert(0, a1 % 2)
			a1 = a1 // 2

		if len(_before) > self._MAXIMUM_HARACTERISE:  # +/- inf
			result[0] = sign
			self._set_exp(result, self._MAXIMUM_HARACTERISE)
		else:
			_after = []

			while a2 and len(_after) < self._HARACTERISE_SHIFT + self._MANTISE_BIT_LENGTH + 1:
				a2 *= 2
				_after.append(a2 // _divider)
				a2 %= _divider

			if _before:
				exponent = len(_before) - 1  # |number| >= 1
				result[0] = sign
				self._set_exp(result, exponent)
				temp = _before[1:] + _after
				for i in range(min(len(temp), self._MANTISE_BIT_LENGTH)):
					result[1 + self._HARACTERISE_BIT_LENGTH + i] = temp[i]
			else:
				exponent = -1

				for i in range(len(_after)):
					if _after[i] == 1:
						exponent = i + 1
						break

				if exponent == -1 or exponent > self._HARACTERISE_SHIFT + self._MANTISE_BIT_LENGTH:  # +/- 0.0
					result[0] = sign
				elif exponent > self._HARACTERISE_SHIFT:  # denormalized
					result[0] = sign
					for i in range(min(len(_after) - self._HARACTERISE_SHIFT, self._MANTISE_BIT_LENGTH)):
						result[1 + self._HARACTERISE_BIT_LENGTH + i] = _after[self._HARACTERISE_SHIFT + i]
				else:  # |number| < 1
					result[0] = sign
					self._set_exp(result, -exponent)
					for i in range(min(len(_after) - exponent, self._MANTISE_BIT_LENGTH)):
						result[1 + self._HARACTERISE_BIT_LENGTH + i] = _after[exponent + i]

		return result


	def show_info(self):
		#print(f's {"e" * self._HARACTERISE_BIT_LENGTH} M.{"m" * self._MANTISE_BIT_LENGTH} decimal value')

		z = [0] + [0] * (self._HARACTERISE_BIT_LENGTH - 1) + [1] + [0] * self._MANTISE_BIT_LENGTH
		print(f'\n[мінімальне за абсолютною величиною ненульове представлення:]\n	{self.ieee754_to_str(z):70}')

		z = [0] + [1] * (self._HARACTERISE_BIT_LENGTH - 1) + [0] + [1] * self._MANTISE_BIT_LENGTH
		print(f'\n[максимальне додатнє представлення (2 - 2^(-{self._MANTISE_BIT_LENGTH})) * 2^{self._MAXIMUM_HARACTERISE - 1}]\n	{self.ieee754_to_str(z):70}')

		z = [1] + [1] * (self._HARACTERISE_BIT_LENGTH - 1) + [0] + [1] * self._MANTISE_BIT_LENGTH
		print(f'\n[мінімальне від’ємне преставлення]\n	{self.ieee754_to_str(z):70}')

		z = self.str_to_ieee754("1.0")
		print(f'\n[число +1,0Е0:]\n	{self.ieee754_to_str(z):70}')

		z = [0] + [1] * self._HARACTERISE_BIT_LENGTH + [0] * self._MANTISE_BIT_LENGTH
		print(f'\n[значення +∞:]\n{self.ieee754_to_str(z):70} ')

		z = [1] + [1] * self._HARACTERISE_BIT_LENGTH + [0] * self._MANTISE_BIT_LENGTH
		print(f'\n[значення -∞:]\n{self.ieee754_to_str(z):70} ')

		z = [0] + [0] * (self._HARACTERISE_BIT_LENGTH ) + [0] * (self._MANTISE_BIT_LENGTH - 1) + [1]
		print(f'\n[будь-який варіант для ненормалізованого ЧПТ:]\n	{self.ieee754_to_str(z):70} ')

		z = [0] + [0] * (self._HARACTERISE_BIT_LENGTH + self._MANTISE_BIT_LENGTH )
		print(f'\n[+0.0]\n{self.ieee754_to_str(z):70}')

		z = [1] + [0] * (self._HARACTERISE_BIT_LENGTH + self._MANTISE_BIT_LENGTH )
		print(f'\n[-0.0]\n{self.ieee754_to_str(z):70} ')

		z = [0] + [1] * (self._HARACTERISE_BIT_LENGTH ) + [0] * (self._MANTISE_BIT_LENGTH - 1) + [1]
		print(f'\n[будь-який варіант для NaN-значення:]\n{self.ieee754_to_str(z):70} ')


	@staticmethod
	def comb_str(s: list) -> str:
		return "".join(map(str,s))


	def __str__(self):
		return f"{self.sign} {self.comb_str(self.haracterise)} {self.comb_str(self.mantise)}"

	def __str_hex__(self):
		return hex(int(self.comb_str([self.sign, *self.haracterise, *self.mantise])))[2:].zfill(2)

	"""Algoritmic operation"""

	def F(self, value):
		if isinstance(value, IEEE754):
			a = self.ieee754_to_float([self.sign]+self.haracterise+self.mantise)
			b = self.ieee754_to_float([value.sign]+value.haracterise+value.mantise)

			result = IEEE754(str(b-a/b+1.5/(a*b)))
			return result
		else:
			return NotImplemented


	def __add__(self, value):
		if isinstance(value, IEEE754):
			val1 = self.ieee754_to_float([self.sign]+self.haracterise+self.mantise)
			val2 = self.ieee754_to_float([value.sign]+value.haracterise+value.mantise)

			result = IEEE754(str(val1+val2))
			return result
		else:
			return NotImplemented


	def __sub__(self, value):
		if isinstance(value, IEEE754):
			val1 = self.ieee754_to_float([self.sign]+self.haracterise+self.mantise)
			val2 = self.ieee754_to_float([value.sign]+value.haracterise+value.mantise)

			result = IEEE754(str(val1-val2))
			return result
		else:
			return NotImplemented


	def __mul__(self, value):
		if isinstance(value, IEEE754):
			val1 = self.ieee754_to_float([self.sign]+self.haracterise+self.mantise)
			val2 = self.ieee754_to_float([value.sign]+value.haracterise+value.mantise)

			result = IEEE754(str(val1*val2))
			return result
		else:
			return NotImplemented


	def __truediv__(self, value):
		if isinstance(value, IEEE754):
			val1 = self.ieee754_to_float([self.sign]+self.haracterise+self.mantise)
			val2 = self.ieee754_to_float([value.sign]+value.haracterise+value.mantise)

			result = IEEE754(str(val1/val2))
			return result
		else:
			return NotImplemented


	def _upd_inner_bit_view(self, ieee754_val):
		self.sign = ieee754_val[0]
		self.haracterise = ieee754_val[1:self._HARACTERISE_BIT_LENGTH + 1]
		self.mantise = ieee754_val[self._HARACTERISE_BIT_LENGTH + 1:]


	def __init__(self, value: str, /, haracterise_length: int = None, mantise_length: int = None):

		if haracterise_length is not None:
			self._HARACTERISE_BIT_LENGTH = haracterise_length
		
		if mantise_length is not None:
			self._MANTISE_BIT_LENGTH = mantise_length

		self._SUMMARY_BIT_LENGTH = 1 + self._HARACTERISE_BIT_LENGTH + self._MANTISE_BIT_LENGTH
		self._HARACTERISE_SHIFT = 2 ** (self._HARACTERISE_BIT_LENGTH - 1) - 1
		self._MAXIMUM_HARACTERISE = 2 ** self._HARACTERISE_BIT_LENGTH - 1 - self._HARACTERISE_SHIFT
		self._MINIMUM_HARACTERISE = -self._HARACTERISE_SHIFT


		ieee754_val = self.str_to_ieee754(value)
		self._upd_inner_bit_view(ieee754_val)

