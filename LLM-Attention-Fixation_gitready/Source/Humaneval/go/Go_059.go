
// Return the largest prime factor of n. Assume n > 1 and is not a prime.
// >>> LargestPrimeFactor(13195)
// 29
// >>> LargestPrimeFactor(2048)
// 2
func LargestPrimeFactor(n int) int {

    isPrime := func(n int) bool {
        for i := 2; i < int(math.Pow(float64(n), 0.5)+1); i++ {
            if n%i == 0 {
                return false
            }
        }
        return true
    }

    largest := 1
    for j := 2; j < n + 1; j++ {
		if n % j == 0 && isPrime(j) {
			if j > largest {
				largest = j
			}
		}
	}
    return largest
}

func TestLargestPrimeFactor(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(5, LargestPrimeFactor(15))
    assert.Equal(3, LargestPrimeFactor(27))
    assert.Equal(7, LargestPrimeFactor(63))
    assert.Equal(11, LargestPrimeFactor(330))
    assert.Equal(29, LargestPrimeFactor(13195))
}
