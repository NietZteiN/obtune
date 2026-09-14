import (
    "fmt"
    "sort"
)

// In this Kata, you have to sort an array of non-negative integers according to
// number of ones in their binary representation in ascending order.
// For similar number of ones, sort based on decimal value.
// 
// It must be implemented like this:
// >>> SortArray([1, 5, 2, 3, 4]) == [1, 2, 3, 4, 5]
// >>> SortArray([-2, -3, -4, -5, -6]) == [-6, -5, -4, -3, -2]
// >>> SortArray([1, 0, 2, 3, 4]) [0, 1, 2, 3, 4]
func SortArray(arr []int) []int {

    sort.Slice(arr, func(i, j int) bool {
        return arr[i] < arr[j]
    })
    sort.Slice(arr, func(i, j int) bool {
        key := func(x int) int {
            b := fmt.Sprintf("%b", x)
            cnt := 0
            for _, r := range b {
                if r == '1' {
                    cnt++
                }
            }
            return cnt
        }
        return key(arr[i]) < key(arr[j])
    })
    return arr
}

func TestSortArray(t *testing.T) {
    assert := assert.New(t)
    assert.Equal([]int{1, 2, 4, 3, 5}, SortArray([]int{1,5,2,3,4}))
    assert.Equal([]int{-4, -2, -6, -5, -3}, SortArray([]int{-2,-3,-4,-5,-6}))
    assert.Equal([]int{0, 1, 2, 4, 3}, SortArray([]int{1,0,2,3,4}))
    assert.Equal([]int{}, SortArray([]int{}))
    assert.Equal([]int{2, 2, 4, 4, 3, 3, 5, 5, 5, 7, 77}, SortArray([]int{2,5,77,4,5,3,5,7,2,3,4}))
    assert.Equal([]int{32, 3, 5, 6, 12, 44}, SortArray([]int{3,6,44,12,32,5}))
    assert.Equal([]int{2, 4, 8, 16, 32}, SortArray([]int{2,4,8,16,32}))
    assert.Equal([]int{2, 4, 8, 16, 32}, SortArray([]int{2,4,8,16,32}))
}
