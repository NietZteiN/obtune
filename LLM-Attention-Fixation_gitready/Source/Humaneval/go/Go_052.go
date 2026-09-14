
// Return true if all numbers in the list l are below threshold t.
// >>> BelowThreshold([1, 2, 4, 10], 100)
// true
// >>> BelowThreshold([1, 20, 4, 10], 5)
// false
func BelowThreshold(l []int,t int) bool {

    for _, n := range l {
		if n >= t {
			return false
		}
	}
	return true
}

func TestBelowThreshold(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(true, BelowThreshold([]int{1, 2, 4, 10}, 100))
    assert.Equal(false, BelowThreshold([]int{1, 20, 4, 10}, 5))
    assert.Equal(true, BelowThreshold([]int{1, 20, 4, 10}, 21))
    assert.Equal(true, BelowThreshold([]int{1, 20, 4, 10}, 22))
    assert.Equal(true, BelowThreshold([]int{1, 8, 4, 10}, 11))
    assert.Equal(false, BelowThreshold([]int{1, 8, 4, 10}, 10))
}
