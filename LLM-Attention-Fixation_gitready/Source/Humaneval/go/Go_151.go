import (
    "math"
)

// Given a list of numbers, return the sum of squares of the numbers
// in the list that are odd. Ignore numbers that are negative or not integers.
// 
// DoubleTheDifference([1, 3, 2, 0]) == 1 + 9 + 0 + 0 = 10
// DoubleTheDifference([-1, -2, 0]) == 0
// DoubleTheDifference([9, -2]) == 81
// DoubleTheDifference([0]) == 0
// 
// If the input list is empty, return 0.
func DoubleTheDifference(lst []float64) int {

    sum := 0
    for _, i := range lst {
        if i > 0 && math.Mod(i, 2) != 0 && i == float64(int(i)) {
            sum += int(math.Pow(i, 2))
        }
    }
    return sum
}

func TestDoubleTheDifference(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(0, DoubleTheDifference([]float64{}))
    assert.Equal(25, DoubleTheDifference([]float64{5, 4}))
    assert.Equal(0, DoubleTheDifference([]float64{0.1, 0.2, 0.3}))
    assert.Equal(0, DoubleTheDifference([]float64{-10, -20, -30}))
    assert.Equal(0, DoubleTheDifference([]float64{-1, -2, 8}))
    assert.Equal(34, DoubleTheDifference([]float64{0.2, 3, 5}))
    lst := make([]float64, 0)
    odd_sum := 0
    var i float64
    for i = -99; i < 100; i+= 2 {
        lst = append(lst, float64(i))
        if math.Mod(i, 2) != 0 && i > 0 {
            odd_sum +=int(math.Pow(i, 2))
        }
    }
    assert.Equal(odd_sum, DoubleTheDifference(lst))
}
