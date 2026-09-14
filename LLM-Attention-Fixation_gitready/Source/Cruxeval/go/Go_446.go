package f_test

import (
    "testing"
    "fmt"
)

func f(array []int) []int {
    l := len(array)
    if l % 2 == 0 {
        array = nil
    } else {
        for i, j := 0, l-1; i < j; i, j = i+1, j-1 {
            array[i], array[j] = array[j], array[i]
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
     { actual: candidate([]int{}), expected: []int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
