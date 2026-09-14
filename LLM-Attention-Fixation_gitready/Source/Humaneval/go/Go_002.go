import (
    "math"
)

// Given a positive floating point number, it can be decomposed into
// and integer part (largest integer smaller than given number) and decimals
// (leftover part always smaller than 1).
// 
// Return the decimal part of the number.
// >>> TruncateNumber(3.5)
// 0.5
func TruncateNumber(number float64) float64 {

    return math.Mod(number,1)
}

func TestTruncateNumber(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(0.5, TruncateNumber(3.5))
    assert.Equal(true, math.Abs(TruncateNumber(1.33)-0.33) < 1e-6)
    assert.Equal(true, math.Abs(TruncateNumber(123.456)-0.456) < 1e-6)
}
