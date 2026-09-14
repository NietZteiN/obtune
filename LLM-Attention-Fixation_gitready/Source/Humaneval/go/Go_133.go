import (
    "math"
)

// You are given a list of numbers.
// You need to return the sum of squared numbers in the given list,
// round each element in the list to the upper int(Ceiling) first.
// Examples:
// For lst = [1,2,3] the output should be 14
// For lst = [1,4,9] the output should be 98
// For lst = [1,3,5,7] the output should be 84
// For lst = [1.4,4.2,0] the output should be 29
// For lst = [-2.4,1,1] the output should be 6
func SumSquares(lst []float64) int {

    squared := 0
    for _, i := range lst {
        squared += int(math.Pow(math.Ceil(i), 2))
    }
    return squared
}

func TestSumSquares(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(14, SumSquares([]float64{1,2,3}))
    assert.Equal(14, SumSquares([]float64{1.0,2,3}))
    assert.Equal(84, SumSquares([]float64{1,3,5,7}))
    assert.Equal(29, SumSquares([]float64{1.4,4.2,0}))
    assert.Equal(6, SumSquares([]float64{-2.4,1,1}))
    assert.Equal(10230, SumSquares([]float64{100,1,15,2}))
    assert.Equal(200000000, SumSquares([]float64{10000,10000}))
    assert.Equal(75, SumSquares([]float64{-1.4,4.6,6.3}))
    assert.Equal(1086, SumSquares([]float64{-1.4,17.9,18.9,19.9}))
    assert.Equal(0, SumSquares([]float64{0}))
    assert.Equal(1, SumSquares([]float64{-1}))
    assert.Equal(2, SumSquares([]float64{-1,1,0}))
}
