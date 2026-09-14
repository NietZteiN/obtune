import (
    "math"
)

// Given a positive integer n, return the count of the numbers of n-digit
// positive integers that start or end with 1.
func StartsOneEnds(n int) int {

    if n == 1 {
        return 1
    }
    return 18 * int(math.Pow(10, float64(n-2)))
}

func TestStartsOneEnds(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(1, StartsOneEnds(1))
    assert.Equal(18, StartsOneEnds(2))
    assert.Equal(180, StartsOneEnds(3))
    assert.Equal(1800, StartsOneEnds(4))
    assert.Equal(18000, StartsOneEnds(5))
}
