import (
    "math"
)

// Given an array of integers nums, find the minimum sum of any non-empty sub-array
// of nums.
// Example
// Minsubarraysum([2, 3, 4, 1, 2, 4]) == 1
// Minsubarraysum([-1, -2, -3]) == -6
func Minsubarraysum(nums []int) int {

    max_sum := 0
    s := 0
    for _, num := range nums {
        s += -num
        if s < 0 {
            s = 0
        }
        if s > max_sum {
            max_sum = s
        }
    }
    if max_sum == 0 {
        max_sum = math.MinInt
        for _, i := range nums {
            if -i > max_sum {
                max_sum = -i
            }
        }
    }
    return -max_sum
}

func TestMinSubArraySum(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(1, Minsubarraysum([]int{2, 3, 4, 1, 2, 4}))
    assert.Equal(-6, Minsubarraysum([]int{-1, -2, -3}))
    assert.Equal(-14, Minsubarraysum([]int{-1, -2, -3, 2, -10}))
    assert.Equal(-9999999999999999, Minsubarraysum([]int{-9999999999999999}))
    assert.Equal(0, Minsubarraysum([]int{0, 10, 20, 1000000}))
    assert.Equal(-6, Minsubarraysum([]int{-1, -2, -3, 10, -5}))
    assert.Equal(-6, Minsubarraysum([]int{100, -1, -2, -3, 10, -5}))
    assert.Equal(3, Minsubarraysum([]int{10, 11, 13, 8, 3, 4}))
    assert.Equal(-33, Minsubarraysum([]int{100, -33, 32, -1, 0, -2}))
    assert.Equal(-10, Minsubarraysum([]int{-10}))
    assert.Equal(7, Minsubarraysum([]int{7}))
    assert.Equal(-1, Minsubarraysum([]int{1, -1}))
}
