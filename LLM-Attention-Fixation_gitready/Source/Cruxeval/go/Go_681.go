package f_test

import (
    "testing"
    "fmt"
)

func f(array []int, ind int, elem int) []int {
    index := ind
    if ind < 0 {
        index = -5
    } else if ind > len(array) {
        index = len(array)
    } else {
        index = ind + 1
    }

    result := make([]int, len(array)+1)
    copy(result[:index], array[:index])
    result[index] = elem
    copy(result[index+1:], array[index:])
    
    return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 5, 8, 2, 0, 3}, 2, 7), expected: []int{1, 5, 8, 7, 2, 0, 3} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
