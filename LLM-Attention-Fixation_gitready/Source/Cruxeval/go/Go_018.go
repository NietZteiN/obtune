package f_test

import (
    "testing"
    "fmt"
)

func f(array []int, elem int) []int {
    var k int
    l := make([]int, len(array))
    copy(l, array)
    for i := range l {
        if l[i] > elem {
            array = append(array[:i], append([]int{elem}, array[i:]...)...)
            break
        }
        k++
    }
    return array
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{5, 4, 3, 2, 1, 0}, 3), expected: []int{3, 5, 4, 3, 2, 1, 0} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
