import (
    "sort"
)

// This function takes a list l and returns a list l' such that
// l' is identical to l in the indicies that are not divisible by three, while its values at the indicies that are divisible by three are equal
// to the values of the corresponding indicies of l, but sorted.
// >>> SortThird([1, 2, 3])
// [1, 2, 3]
// >>> SortThird([5, 6, 3, 4, 8, 9, 2])
// [2, 6, 3, 4, 8, 9, 5]
func SortThird(l []int) []int {

    temp := make([]int, 0)
	for i := 0; i < len(l); i = i + 3 {
		temp = append(temp, l[i])
	}
	sort.Ints(temp)
	j := 0
	for i := 0; i < len(l); i = i + 3 {
		l[i] = temp[j]
		j++
	}
	return l
}

func TestSortThird(t *testing.T) {
    assert := assert.New(t)
	same := func(src []int, target []int) bool {
		for i := 0; i < len(src); i++ {
			if src[i] != target[i] {
				return false
			}
		}
		return true
	}
	assert.Equal(true, same([]int{1, 2, 3}, SortThird([]int{1, 2, 3})))
	assert.Equal(true, same([]int{1, 3, -5, 2, -3, 3, 5, 0, 123, 9, -10}, SortThird([]int{5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10})))
	assert.Equal(true, same([]int{-10, 8, -12,3, 23, 2, 4, 11, 12, 5}, SortThird([]int{5, 8, -12, 4, 23, 2, 3, 11, 12, -10})))
	assert.Equal(true, same([]int{2, 6, 3, 4, 8, 9, 5}, SortThird([]int{5, 6, 3, 4, 8, 9, 2})))
	assert.Equal(true, same([]int{2, 8, 3, 4, 6, 9, 5}, SortThird([]int{5, 8, 3, 4, 6, 9, 2})))
	assert.Equal(true, same([]int{2, 6, 9, 4, 8, 3, 5}, SortThird([]int{5, 6, 9, 4, 8, 3, 2})))
	assert.Equal(true, same([]int{2, 6, 3, 4, 8, 9, 5, 1}, SortThird([]int{5, 6, 3, 4, 8, 9, 2, 1})))
}
