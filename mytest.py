import sys
	
def test(did_pass):
	""" Print the result of a test """
	linenum=sys._getframe(1).f_lineno
	if did_pass:
		msg="Test at line {0} PASSED.".format(linenum)
	else:
		msg="Test at line {0} FAILED.".format(linenum)
	
	print(msg)


if __name__ == "__main__":
	def absolute_value(x):
		if x < 0:
			return -x
		return x


	def bad_absolute_value(x):
		if x < 0:
			return -x
		elif x > 0:
			return x


	def absfun_test_suite(fun):
		test(fun(17) == 17)
		test(fun(-17) == 17)
		test(fun(0) == 0)
		test(fun(3.14) == 3.14)
		test(fun(-3.14) == 3.14)
		test(fun(0.0) == 0.0)

	print("Testing absolute_value:")
	absfun_test_suite(absolute_value)

	print("Testing bad_absolute_value:")
	absfun_test_suite(bad_absolute_value)
