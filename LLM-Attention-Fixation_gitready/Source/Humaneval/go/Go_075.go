
// Write a function that returns true if the given number is the multiplication of 3 prime numbers
// and false otherwise.
// Knowing that (a) is less then 100.
// Example:
// IsMultiplyPrime(30) == true
// 30 = 2 * 3 * 5
func IsMultiplyPrime(a int) bool {

    isPrime := func(n int) bool {
        for i := 2; i < int(math.Pow(float64(n), 0.5)+1); i++ {
            if n%i == 0 {
                return false
            }
        }
        return true
    }
    for i := 2; i < 101; i++ {
		if !isPrime(i) {
			continue
		}
		for j := 2; j < 101; j++ {
			if !isPrime(j) {
				continue
			}
			for k := 2; k < 101; k++ {
				if !isPrime(k) {
					continue
				}
				if i*j*k == a {
					return true
				}
			}
		}
	}
	return false
}

func TestIsMultiplyPrime(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(false, IsMultiplyPrime(5))
    assert.Equal(true, IsMultiplyPrime(30))
    assert.Equal(true, IsMultiplyPrime(8))
    assert.Equal(false, IsMultiplyPrime(10))
    assert.Equal(true, IsMultiplyPrime(125))
    assert.Equal(true, IsMultiplyPrime(3 * 5 * 7))
    assert.Equal(false, IsMultiplyPrime(3 * 6 * 7))
    assert.Equal(false, IsMultiplyPrime(9 * 9 * 9))
    assert.Equal(false, IsMultiplyPrime(11 * 9 * 9))
    assert.Equal(true, IsMultiplyPrime(11 * 13 * 7))
}
