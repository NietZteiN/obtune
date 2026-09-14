package f_test

import (
    "testing"
    "fmt"
)

func f(array []int) []int {
    for i := 0; i < len(array); {
        if array[i] == -1 {
            array = append(array[:i], array[i+1:]...)
        } else if array[i] == 0 {
            array = array[:len(array)-1]
        } else if array[i] == 1 {
            array = array[1:]
        } else {
            i++
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
     { actual: candidate([]int{0, 2}), expected: []int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
