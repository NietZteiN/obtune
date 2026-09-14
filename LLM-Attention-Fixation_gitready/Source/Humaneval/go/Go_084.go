import (
    "fmt"
    "strconv"
)

// Given a positive integer N, return the total sum of its digits in binary.
// 
// Example
// For N = 1000, the sum of digits will be 1 the output should be "1".
// For N = 150, the sum of digits will be 6 the output should be "110".
// For N = 147, the sum of digits will be 12 the output should be "1100".
// 
// Variables:
// @N integer
// Constraints: 0 ≤ N ≤ 10000.
// Output:
// a string of binary number
func Solve(N int) string {

    sum := 0
    for _, c := range strconv.Itoa(N) {
        sum += int(c - '0')
    }
    return fmt.Sprintf("%b", sum)
}

func TestSolve(t *testing.T) {
    assert := assert.New(t)
    assert.Equal("1", Solve(1000), "Error")
    assert.Equal("110", Solve(150), "Error")
    assert.Equal("1100", Solve(147), "Error")
    assert.Equal("1001", Solve(333), "Error")
    assert.Equal("10010", Solve(963), "Error")
}
