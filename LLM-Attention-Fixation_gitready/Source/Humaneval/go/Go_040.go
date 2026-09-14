
// TriplesSumToZero takes a list of integers as an input.
// it returns true if there are three distinct elements in the list that
// sum to zero, and false otherwise.
// 
// >>> TriplesSumToZero([1, 3, 5, 0])
// false
// >>> TriplesSumToZero([1, 3, -2, 1])
// true
// >>> TriplesSumToZero([1, 2, 3, 7])
// false
// >>> TriplesSumToZero([2, 4, -5, 3, 9, 7])
// true
// >>> TriplesSumToZero([1])
// false
func TriplesSumToZero(l []int) bool {

    for i := 0; i < len(l) - 2; i++ {
		for j := i + 1; j < len(l) - 1; j++ {
			for k := j + 1; k < len(l); k++ {
				if l[i] + l[j] + l[k] == 0 {
					return true
				}
			}
		}
	}
	return false
}

func TestTriplesSumToZero(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(false, TriplesSumToZero([]int{1, 3, 5, 0}))
    assert.Equal(false, TriplesSumToZero([]int{1, 3, 5, -1}))
    assert.Equal(true, TriplesSumToZero([]int{1, 3, -2, 1}))
    assert.Equal(false, TriplesSumToZero([]int{1, 2, 3, 7}))
    assert.Equal(false, TriplesSumToZero([]int{1, 2, 5, 7}))
    assert.Equal(true, TriplesSumToZero([]int{2, 4, -5, 3, 9, 7}))
    assert.Equal(false, TriplesSumToZero([]int{1}))
    assert.Equal(false, TriplesSumToZero([]int{1, 3, 5, -100}))
    assert.Equal(false, TriplesSumToZero([]int{100, 3, 5, -100}))
}
