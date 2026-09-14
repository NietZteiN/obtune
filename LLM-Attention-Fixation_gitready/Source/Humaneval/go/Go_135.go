
// Create a function which returns the largest index of an element which
// is not greater than or equal to the element immediately preceding it. If
// no such element exists then return -1. The given array will not contain
// duplicate values.
// 
// Examples:
// CanArrange([1,2,4,3,5]) = 3
// CanArrange([1,2,3]) = -1
func CanArrange(arr []int) int {

    ind:=-1
    i:=1
    for i<len(arr) {
      if arr[i]<arr[i-1] {
        ind=i
      }
      i++
    }
    return ind
}

func TestCanArrange(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(3, CanArrange([]int{1,2,4,3,5}))
    assert.Equal(-1, CanArrange([]int{1,2,4,5}))
    assert.Equal(2, CanArrange([]int{1,4,2,5,6,7,8,9,10}))
    assert.Equal(4, CanArrange([]int{4,8,5,7,3}))
    assert.Equal(-1, CanArrange([]int{}))
}
