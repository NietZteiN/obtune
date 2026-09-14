
// A simple program which should return the value of x if n is
// a prime number and should return the value of y otherwise.
// 
// Examples:
// for XOrY(7, 34, 12) == 34
// for XOrY(15, 8, 5) == 5
func XOrY(n, x, y int) int {

    if n == 1 {
        return y
    }
    for i := 2;i < n;i++ {
        if n % i == 0 {
            return y
        }
    }
    return x
}

func TestXOrY(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(34, XOrY(7, 34, 12))
    assert.Equal(5, XOrY(15, 8, 5))
    assert.Equal(33, XOrY(3, 33, 5212))
    assert.Equal(3, XOrY(1259, 3, 52))
    assert.Equal(-1, XOrY(7919, -1, 12))
    assert.Equal(583, XOrY(3609, 1245, 583))
    assert.Equal(129, XOrY(91, 56, 129))
    assert.Equal(1234, XOrY(6, 34, 1234))
    assert.Equal(0, XOrY(1, 2, 0))
    assert.Equal(2, XOrY(2, 2, 0))
}
