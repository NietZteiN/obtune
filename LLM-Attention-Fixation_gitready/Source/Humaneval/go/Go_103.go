import (
    "fmt"
    "math"
)

// You are given two positive integers n and m, and your task is to compute the
// average of the integers from n through m (including n and m).
// Round the answer to the nearest integer and convert that to binary.
// If n is greater than m, return -1.
// Example:
// RoundedAvg(1, 5) => "0b11"
// RoundedAvg(7, 5) => -1
// RoundedAvg(10, 20) => "0b1111"
// RoundedAvg(20, 33) => "0b11010"
func RoundedAvg(n, m int) interface{} {

    if m < n {
        return -1
    }
    summation := 0
    for i := n;i < m+1;i++{
        summation += i
    }
    return fmt.Sprintf("0b%b", int(math.Round(float64(summation)/float64(m - n + 1))))
}

func TestRoundedAvg(t *testing.T) {
    assert := assert.New(t)
    assert.Equal("0b11", RoundedAvg(1, 5))
    assert.Equal("0b1010", RoundedAvg(7, 13))
    assert.Equal("0b1111001011", RoundedAvg(964, 977))
    assert.Equal("0b1111100101", RoundedAvg(996, 997))
    assert.Equal("0b1011000010", RoundedAvg(560, 851))
    assert.Equal("0b101101110", RoundedAvg(185, 546))
    assert.Equal("0b110101101", RoundedAvg(362, 496))
    assert.Equal("0b1001110010", RoundedAvg(350, 902))
    assert.Equal("0b11010111", RoundedAvg(197, 233))
    assert.Equal(-1, RoundedAvg(7, 5))
    assert.Equal(-1, RoundedAvg(5, 1))
    assert.Equal("0b101", RoundedAvg(5, 5))
}
