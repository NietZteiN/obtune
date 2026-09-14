import (
	"math"
)

// PrimeFib returns n-th number that is a Fibonacci number and it's also prime.
// >>> PrimeFib(1)
// 2
// >>> PrimeFib(2)
// 3
// >>> PrimeFib(3)
// 5
// >>> PrimeFib(4)
// 13
// >>> PrimeFib(5)
// 89
func PrimeFib(n int) int {

    isPrime := func(p int) bool {
		if p < 2 {
			return false
		}
		for i := 2; i < int(math.Min(math.Sqrt(float64(p))+1, float64(p-1))); i++ {
			if p%i == 0 {
				return false
			}
		}
		return true
	}
	f := []int{0, 1}
	for {
		f = append(f, f[len(f)-1]+f[len(f)-2])
		if isPrime(f[len(f)-1]) {
			n -= 1
		}
		if n == 0 {
			return f[len(f)-1]
		}
	}
}

func TestPrimeFib(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(2, PrimeFib(1))
    assert.Equal(3, PrimeFib(2))
    assert.Equal(5, PrimeFib(3))
    assert.Equal(13, PrimeFib(4))
    assert.Equal(89, PrimeFib(5))
    assert.Equal(233, PrimeFib(6))
    assert.Equal(1597, PrimeFib(7))
    assert.Equal(28657, PrimeFib(8))
    assert.Equal(514229, PrimeFib(9))
    assert.Equal(433494437, PrimeFib(10))
}
