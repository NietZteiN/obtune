
// Your task is to write a function that returns true if a number x is a simple
// power of n and false in other cases.
// x is a simple power of n if n**int=x
// For example:
// IsSimplePower(1, 4) => true
// IsSimplePower(2, 2) => true
// IsSimplePower(8, 2) => true
// IsSimplePower(3, 2) => false
// IsSimplePower(3, 1) => false
// IsSimplePower(5, 3) => false
func IsSimplePower(x int,n int) bool {

    if x == 1 {
		return true
	}
	if n==1 {
		return false
	}
	if x % n != 0 {
		return false
	}
	return IsSimplePower(x / n, n)
}

func TestIsSimplePower(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(true, IsSimplePower(1, 4))
    assert.Equal(true, IsSimplePower(2, 2))
    assert.Equal(true, IsSimplePower(8, 2))
    assert.Equal(false, IsSimplePower(3, 2))
    assert.Equal(false, IsSimplePower(3, 1))
    assert.Equal(false, IsSimplePower(5, 3))
    assert.Equal(true, IsSimplePower(16, 2))
    assert.Equal(false, IsSimplePower(143214, 16))
    assert.Equal(true, IsSimplePower(4, 2))
    assert.Equal(true, IsSimplePower(9, 3))
    assert.Equal(true, IsSimplePower(16, 4))
    assert.Equal(false, IsSimplePower(24, 2))
    assert.Equal(false, IsSimplePower(128, 4))
    assert.Equal(false, IsSimplePower(12, 6))
    assert.Equal(true, IsSimplePower(1, 1))
    assert.Equal(true, IsSimplePower(1, 12))
}
