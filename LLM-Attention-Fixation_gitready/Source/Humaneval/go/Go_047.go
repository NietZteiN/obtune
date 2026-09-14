import (
	"sort"
)

// Return Median of elements in the list l.
// >>> Median([3, 1, 2, 4, 5])
// 3.0
// >>> Median([-10, 4, 6, 1000, 10, 20])
// 15.0
func Median(l []int) float64 {

    sort.Ints(l)
	if len(l)%2==1{
		return float64(l[len(l)/2])
	}else{
		return float64(l[len(l)/2-1]+l[len(l)/2])/2.0
	}
}

func TestMedian(t *testing.T) {
	assert := assert.New(t)
	assert.Equal(3.0, Median([]int{3, 1, 2, 4, 5}))
	assert.Equal(8.0, Median([]int{-10, 4, 6, 1000, 10, 20}))
	assert.Equal(5.0, Median([]int{5}))
	assert.Equal(5.5, Median([]int{6, 5}))
	assert.Equal(7.0, Median([]int{8, 1, 3, 9, 9, 2, 7}))
}
