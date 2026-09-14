import (
    "math"
)

// You are given an array arr of integers and you need to return
// sum of magnitudes of integers multiplied by product of all signs
// of each number in the array, represented by 1, -1 or 0.
// Note: return nil for empty arr.
// 
// Example:
// >>> ProdSigns([1, 2, 2, -4]) == -9
// >>> ProdSigns([0, 1]) == 0
// >>> ProdSigns([]) == nil
func ProdSigns(arr []int) interface{} {

    if len(arr) == 0 {
        return nil
    }
    cnt := 0
    sum := 0
    for _, i := range arr {
        if i == 0 {
            return 0
        }
        if i < 0 {
            cnt++
        }
        sum += int(math.Abs(float64(i)))
    }

    prod := int(math.Pow(-1, float64(cnt)))
    return prod * sum
}

func TestProdSigns(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(-9, ProdSigns([]int{1, 2, 2, -4}))
    assert.Equal(0, ProdSigns([]int{0, 1}))
    assert.Equal(-10, ProdSigns([]int{1, 1, 1, 2, 3, -1, 1}))
    assert.Equal(nil, ProdSigns([]int{}))
    assert.Equal(20, ProdSigns([]int{2, 4,1, 2, -1, -1, 9}))
    assert.Equal(4, ProdSigns([]int{-1, 1, -1, 1}))
    assert.Equal(-4, ProdSigns([]int{-1, 1, 1, 1}))
    assert.Equal(0, ProdSigns([]int{-1, 1, 1, 0}))
}
