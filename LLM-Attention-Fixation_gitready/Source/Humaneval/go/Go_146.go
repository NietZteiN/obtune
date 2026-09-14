import (
    "strconv"
)

// Write a function that takes an array of numbers as input and returns
// the number of elements in the array that are greater than 10 and both
// first and last digits of a number are odd (1, 3, 5, 7, 9).
// For example:
// Specialfilter([15, -73, 14, -15]) => 1
// Specialfilter([33, -2, -3, 45, 21, 109]) => 2
func Specialfilter(nums []int) int {

    count := 0
    for _, num := range nums {
        if num > 10 {
            number_as_string := strconv.Itoa(num)
            if number_as_string[0]&1==1 && number_as_string[len(number_as_string)-1]&1==1 {
                count++
            }
        }
    }        
    return count
}

func TestSpecialFilter(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(0, Specialfilter([]int{5, -2, 1, -5}))
    assert.Equal(1, Specialfilter([]int{15, -73, 14, -15}))
    assert.Equal(2, Specialfilter([]int{33, -2, -3, 45, 21, 109}))
    assert.Equal(4, Specialfilter([]int{43, -12, 93, 125, 121, 109}))
    assert.Equal(3, Specialfilter([]int{71, -2, -33, 75, 21, 19}))
    assert.Equal(0, Specialfilter([]int{1}))
    assert.Equal(0, Specialfilter([]int{}))
}
