import (
    "math"
    "strconv"
)

// Write a function CountNums which takes an array of integers and returns
// the number of elements which has a sum of digits > 0.
// If a number is negative, then its first signed digit will be negative:
// e.g. -123 has signed digits -1, 2, and 3.
// >>> CountNums([]) == 0
// >>> CountNums([-1, 11, -11]) == 1
// >>> CountNums([1, 1, 2]) == 3
func CountNums(arr []int) int {

    digits_sum:= func (n int) int {
        neg := 1
        if n < 0 {
             n, neg = -1 * n, -1 
        }
        r := make([]int,0)
        for _, c := range strconv.Itoa(n) {
            r = append(r, int(c-'0'))
        }
        r[0] *= neg
        sum := 0
        for _, i := range r {
            sum += i
        }
        return sum
    }
    count := 0
    for _, i := range arr {
        x := digits_sum(i)
        if x > 0 {
            count++
        }
    }
    return count
}

func TestCountNums(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(0, CountNums([]int{}))
    assert.Equal(0, CountNums([]int{-1, -2, 0}))
    assert.Equal(6, CountNums([]int{1, 1, 2, -2, 3, 4, 5}))
    assert.Equal(5, CountNums([]int{1, 6, 9, -6, 0, 1, 5}))
    assert.Equal(4, CountNums([]int{1, 100, 98, -7, 1, -1}))
    assert.Equal(5, CountNums([]int{12, 23, 34, -45, -56, 0}))
    assert.Equal(1, CountNums([]int{-0, int(math.Pow(1, 0))}))
    assert.Equal(1, CountNums([]int{1}))
}
