
// Given a positive integer n, you have to make a pile of n levels of stones.
// The first level has n stones.
// The number of stones in the next level is:
// - the next odd number if n is odd.
// - the next even number if n is even.
// Return the number of stones in each level in a list, where element at index
// i represents the number of stones in the level (i+1).
// 
// Examples:
// >>> MakeAPile(3)
// [3, 5, 7]
func MakeAPile(n int) []int {

    result := make([]int, 0, n)
    for i := 0; i < n; i++ {
        result = append(result, n+2*i)
    }
    return result
}

func TestMakeAPile(t *testing.T) {
    assert := assert.New(t)
    assert.Equal([]int{3, 5, 7}, MakeAPile(3))
    assert.Equal([]int{4, 6, 8, 10}, MakeAPile(4))
    assert.Equal([]int{5, 7, 9, 11, 13}, MakeAPile(5))
    assert.Equal([]int{6, 8, 10, 12, 14, 16}, MakeAPile(6))
    assert.Equal([]int{8, 10, 12, 14, 16, 18, 20, 22}, MakeAPile(8))
}
