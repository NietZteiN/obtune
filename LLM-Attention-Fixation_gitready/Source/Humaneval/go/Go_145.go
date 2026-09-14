import (
    "sort"
    "strconv"
)

// Write a function which sorts the given list of integers
// in ascending order according to the sum of their digits.
// Note: if there are several items with similar sum of their digits,
// order them based on their index in original list.
// 
// For example:
// >>> OrderByPoints([1, 11, -1, -11, -12]) == [-1, -11, 1, -12, 11]
// >>> OrderByPoints([]) == []
func OrderByPoints(nums []int) []int {

    digits_sum := func (n int) int {
        neg := 1
        if n < 0 {
            n, neg = -1 * n, -1 
        }
        sum := 0
        for i, c := range strconv.Itoa(n) {
            if i == 0 {
                sum += int(c-'0')*neg
            } else {
                sum += int(c-'0')
            }
        }
        return sum
    }
    sort.SliceStable(nums, func(i, j int) bool {
        return digits_sum(nums[i]) < digits_sum(nums[j])
    })
    return nums
}

func TestOrderByPoints(t *testing.T) {
    assert := assert.New(t)
    assert.Equal([]int{-1, -11, 1, -12, 11}, OrderByPoints([]int{1, 11, -1, -11, -12}))
    assert.Equal([]int{0, 2, 3, 6, 53, 423, 423, 423, 1234, 145, 37, 46, 56, 463, 3457}, OrderByPoints([]int{1234,423,463,145,2,423,423,53,6,37,3457,3,56,0,46}))
    assert.Equal([]int{}, OrderByPoints([]int{}))
    assert.Equal([]int{-3, -32, -98, -11, 1, 2, 43, 54}, OrderByPoints([]int{1, -11, -32, 43, 54, -98, 2, -3}))
    assert.Equal([]int{1, 10, 2, 11, 3, 4, 5, 6, 7, 8, 9}, OrderByPoints([]int{1,2,3,4,5,6,7,8,9,10,11}))
    assert.Equal([]int{-76, -21, 0, 4, 23, 6, 6}, OrderByPoints([]int{0,6,6,-76,-21,23,4}))
}
