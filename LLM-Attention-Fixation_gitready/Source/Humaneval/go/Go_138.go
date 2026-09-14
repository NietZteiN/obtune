
// Evaluate whether the given number n can be written as the sum of exactly 4 positive even numbers
// Example
// IsEqualToSumEven(4) == false
// IsEqualToSumEven(6) == false
// IsEqualToSumEven(8) == true
func IsEqualToSumEven(n int) bool {

    return n&1 == 0 && n >= 8
}

func TestIsEqualToSumEven(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(false, IsEqualToSumEven(4))
    assert.Equal(false, IsEqualToSumEven(6))
    assert.Equal(true, IsEqualToSumEven(8))
    assert.Equal(true, IsEqualToSumEven(10))
    assert.Equal(false, IsEqualToSumEven(11))
    assert.Equal(true, IsEqualToSumEven(12))
    assert.Equal(false, IsEqualToSumEven(13))
    assert.Equal(true, IsEqualToSumEven(16))
}
