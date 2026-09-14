
// Return n-th Fibonacci number.
// >>> Fib(10)
// 55
// >>> Fib(1)
// 1
// >>> Fib(8)
// 21
func Fib(n int) int {

    if n <= 1 {
		return n
	}
	return Fib(n-1) + Fib(n-2)
}

func TestFib(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(55, Fib(10))
    assert.Equal(1, Fib(1))
    assert.Equal(21, Fib(8))
    assert.Equal(89, Fib(11))
    assert.Equal(144, Fib(12))
}
