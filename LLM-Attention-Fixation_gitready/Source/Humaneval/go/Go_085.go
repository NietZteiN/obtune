
// Given a non-empty list of integers lst. Add the even elements that are at odd indices..
// 
// Examples:
// Add([4, 2, 6, 7]) ==> 2
func Add(lst []int) int {

    sum := 0
    for i := 1; i < len(lst); i += 2 {
        if lst[i]%2 == 0 {
            sum += lst[i]
        }
    }
    return sum
}

func TestAdd(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(88, Add([]int{4, 88}))
    assert.Equal(122, Add([]int{4, 5, 6, 7, 2, 122}))
    assert.Equal(0, Add([]int{4, 0, 6, 7}))
    assert.Equal(12, Add([]int{4, 4, 6, 8}))
}
