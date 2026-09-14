package f_test

import (
    "testing"
    "fmt"
)

func f(array []int, elem int) []int {
    for idx, e := range array {
        if e > elem && array[idx-1] < elem {
            temp := append([]int{}, array[:idx]...)
            temp = append(temp, elem)
            array = append(temp, array[idx:]...)
        }
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
     { actual: candidate([]int{1, 2, 3, 5, 8}, 6), expected: []int{1, 2, 3, 5, 6, 8} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
