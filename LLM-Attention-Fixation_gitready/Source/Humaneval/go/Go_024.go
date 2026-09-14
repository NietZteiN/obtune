
// For a given number n, find the largest number that divides n evenly, smaller than n
// >>> LargestDivisor(15)
// 5
func LargestDivisor(n int) int {

    for i := n - 1; i > 0; i-- {
		if n % i == 0 {
			return i
		}
	}
	return 0
}

func TestLargestDivisor(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(1, LargestDivisor(3))
    assert.Equal(1, LargestDivisor(7))
    assert.Equal(5, LargestDivisor(10))
    assert.Equal(50, LargestDivisor(100))
    assert.Equal(7, LargestDivisor(49))
}
