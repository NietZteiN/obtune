package f_test

import (
    "testing"
    "fmt"
)

func f(array []int, index int, value int) []int {
    array = append(array[:0], append([]int{index + 1}, array[0:]...)...)
    if value >= 1 {
        array = append(array[:index], append([]int{value}, array[index:]...)...)
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
     { actual: candidate([]int{2}, 0, 2), expected: []int{2, 1, 2} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
