
// For a given list of integers, return a tuple consisting of a sum and a product of all the integers in a list.
// Empty sum should be equal to 0 and empty product should be equal to 1.
// >>> SumProduct([])
// (0, 1)
// >>> SumProduct([1, 2, 3, 4])
// (10, 24)
func SumProduct(numbers []int) [2]int {

    sum_value := 0
    prod_value := 1

    for _, n := range numbers {
        sum_value += n
        prod_value *= n
    }
    return [2]int{sum_value, prod_value}
}

func TestSumProduct(t *testing.T) {
    assert := assert.New(t)
    assert.Equal([2]int{0, 1}, SumProduct([]int{}))
    assert.Equal([2]int{3, 1}, SumProduct([]int{1, 1, 1}))
    assert.Equal([2]int{100, 0}, SumProduct([]int{100, 0}))
    assert.Equal([2]int{3 + 5 + 7, 3 * 5 * 7}, SumProduct([]int{3, 5, 7}))
    assert.Equal([2]int{10, 10}, SumProduct([]int{10}))
}
