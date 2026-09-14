// Filter given list of any values only for integers
// >>> FilterIntegers(['a', 3.14, 5])
// [5]
// >>> FilterIntegers([1, 2, 3, 'abc', {}, []])
// [1, 2, 3]
func FilterIntegers(values []interface{}) []int {

    result := make([]int, 0)
    for _, val := range values {
        switch i := val.(type) {
        case int:
            result = append(result, i)
        }
    }
    return result
}

func TestFilterIntegers(t *testing.T) {
    assert := assert.New(t)
    assert.Equal([]int{}, FilterIntegers([]interface{}{}))
    assert.Equal([]int{4, 9}, FilterIntegers([]interface{}{4, nil, []interface{}{}, 23.2, 9, "adasd"}))
    assert.Equal([]int{3, 3, 3}, FilterIntegers([]interface{}{3, 'c', 3, 3, 'a', 'b'}))
}
