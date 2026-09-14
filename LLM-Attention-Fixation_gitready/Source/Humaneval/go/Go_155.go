import (
    "strconv"
)

// Given an integer. return a tuple that has the number of even and odd digits respectively.
// 
// Example:
// EvenOddCount(-12) ==> (1, 1)
// EvenOddCount(123) ==> (1, 2)
func EvenOddCount(num int) [2]int {

    even_count := 0
    odd_count := 0
    if num < 0 {
        num = -num
    }
    for _, r := range strconv.Itoa(num) {
        if r&1==0 {
            even_count++
        } else {
            odd_count++
        }
    }
    return [2]int{even_count, odd_count}
}

func TestEvenOddCount(t *testing.T) {
    assert := assert.New(t)
    assert.Equal([2]int{0, 1}, EvenOddCount(7))
    assert.Equal([2]int{1, 1}, EvenOddCount(-78))
    assert.Equal([2]int{2, 2}, EvenOddCount(3452))
    assert.Equal([2]int{3, 3}, EvenOddCount(346211))
    assert.Equal([2]int{3, 3}, EvenOddCount(-345821))
    assert.Equal([2]int{1, 0}, EvenOddCount(-2))
    assert.Equal([2]int{2, 3}, EvenOddCount(-45347))
    assert.Equal([2]int{1, 0}, EvenOddCount(0))
}
