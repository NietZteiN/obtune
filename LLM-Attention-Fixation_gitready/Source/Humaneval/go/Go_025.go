import (
    "math"
)

// Return list of prime factors of given integer in the order from smallest to largest.
// Each of the factors should be listed number of times corresponding to how many times it appeares in factorization.
// Input number should be equal to the product of all factors
// >>> Factorize(8)
// [2, 2, 2]
// >>> Factorize(25)
// [5, 5]
// >>> Factorize(70)
// [2, 5, 7]
func Factorize(n int) []int {

    fact := make([]int, 0)
	for i := 2; i <= int(math.Sqrt(float64(n))+1); {
		if n%i == 0 {
			fact = append(fact, i)
			n = n / i
		} else {
			i++
		}
	}
	if n > 1 {
		fact = append(fact, n)
	}
	return fact
}

func TestFactorize(t *testing.T) {
    assert := assert.New(t)
    assert.Equal([]int{2}, Factorize(2))
    assert.Equal([]int{2, 2}, Factorize(4))
    assert.Equal([]int{2, 2, 2}, Factorize(8))
    assert.Equal([]int{3, 19}, Factorize(3 * 19))
    assert.Equal([]int{3, 3, 19, 19}, Factorize(3 * 19 * 3 * 19))
    assert.Equal([]int{3, 3, 3, 19, 19, 19}, Factorize(3 * 19 * 3 * 19 * 3 * 19))
    assert.Equal([]int{3, 19, 19, 19}, Factorize(3 * 19 * 19 * 19))
    assert.Equal([]int{2, 3, 3}, Factorize(3 * 2 * 3))
}
