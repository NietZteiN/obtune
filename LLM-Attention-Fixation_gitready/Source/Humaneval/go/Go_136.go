
// Create a function that returns a tuple (a, b), where 'a' is
// the largest of negative integers, and 'b' is the smallest
// of positive integers in a list.
// If there is no negative or positive integers, return them as nil.
// 
// Examples:
// LargestSmallestIntegers([2, 4, 1, 3, 5, 7]) == (nil, 1)
// LargestSmallestIntegers([]) == (nil, nil)
// LargestSmallestIntegers([0]) == (nil, nil)
func LargestSmallestIntegers(lst []int) [2]interface{}{

    smallest := make([]int, 0)
    largest := make([]int, 0)
    for _, x := range lst {
        if x < 0 {
            smallest = append(smallest, x)
        } else if x > 0 {
            largest = append(largest, x)
        }
    }
    var result [2]interface{}
    if len(smallest) == 0 {
        result[0] = nil
    } else {
        max := smallest[0]
        for i := 1;i < len(smallest);i++ {
            if smallest[i] > max {
                max = smallest[i]
            }
        }
        result[0] = max
    }
    if len(largest) == 0 {
        result[1] = nil
    } else {
        min := largest[0]
        for i := 1;i < len(largest);i++ {
            if largest[i] < min {
                min = largest[i]
            }
        }
        result[1] = min
    }
    return result
}

func TestLargestSmallestIntegers(t *testing.T) {
    assert := assert.New(t)
    assert.Equal([2]interface{}{nil, 1}, LargestSmallestIntegers([]int{2, 4, 1, 3, 5, 7}))
    assert.Equal([2]interface{}{nil, 1}, LargestSmallestIntegers([]int{2, 4, 1, 3, 5, 7, 0}))
    assert.Equal([2]interface{}{-2, 1}, LargestSmallestIntegers([]int{1, 3, 2, 4, 5, 6, -2}))
    assert.Equal([2]interface{}{-7, 2}, LargestSmallestIntegers([]int{4, 5, 3, 6, 2, 7, -7}))
    assert.Equal([2]interface{}{-9, 2}, LargestSmallestIntegers([]int{7, 3, 8, 4, 9, 2, 5, -9}))
    assert.Equal([2]interface{}{nil, nil}, LargestSmallestIntegers([]int{}))
    assert.Equal([2]interface{}{nil, nil}, LargestSmallestIntegers([]int{0}))
    assert.Equal([2]interface{}{-1, nil}, LargestSmallestIntegers([]int{-1, -3, -5, -6}))
    assert.Equal([2]interface{}{-1, nil}, LargestSmallestIntegers([]int{-1, -3, -5, -6, 0}))
    assert.Equal([2]interface{}{-3, 1}, LargestSmallestIntegers([]int{-6, -4, -4, -3, 1}))
    assert.Equal([2]interface{}{-3, 1}, LargestSmallestIntegers([]int{-6, -4, -4, -3, -100, 1}))
}
