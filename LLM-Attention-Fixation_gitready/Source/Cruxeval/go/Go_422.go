package f_test

import (
    "testing"
    "fmt"
)

func f(array []int) []int {
    new_array := make([]int, len(array))
    copy(new_array, array)
    for i, j := 0, len(new_array)-1; i < j; i, j = i+1, j-1 {
        new_array[i], new_array[j] = new_array[j], new_array[i]
    }

    result := make([]int, len(new_array))
    for i, v := range new_array {
        result[i] = v * v
    }

    return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 2, 1}), expected: []int{1, 4, 1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
