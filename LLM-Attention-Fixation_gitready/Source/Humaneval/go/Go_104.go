import (
    "sort"
    "strconv"
)

// Given a list of positive integers x. return a sorted list of all
// elements that hasn't any even digit.
// 
// Note: Returned list should be sorted in increasing order.
// 
// For example:
// >>> UniqueDigits([15, 33, 1422, 1])
// [1, 15, 33]
// >>> UniqueDigits([152, 323, 1422, 10])
// []
func UniqueDigits(x []int) []int {

    odd_digit_elements := make([]int, 0)
    OUTER:
    for _, i := range x {
        for _, c := range strconv.Itoa(i) {
            if (c - '0') % 2 == 0 {
                continue OUTER
            }
        }
            odd_digit_elements = append(odd_digit_elements, i)
    }
    sort.Slice(odd_digit_elements, func(i, j int) bool {
        return odd_digit_elements[i] < odd_digit_elements[j]
    })
    return odd_digit_elements
}

func TestUniqueDigits(t *testing.T) {
    assert := assert.New(t)
    assert.Equal([]int{1, 15, 33}, UniqueDigits([]int{15, 33, 1422, 1}))
    assert.Equal([]int{}, UniqueDigits([]int{152, 323, 1422, 10}))
    assert.Equal([]int{111, 151}, UniqueDigits([]int{12345, 2033, 111, 151}))
    assert.Equal([]int{31, 135}, UniqueDigits([]int{135, 103, 31}))
}
