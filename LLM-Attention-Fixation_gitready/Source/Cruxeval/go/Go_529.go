package f_test

import (
    "testing"
    "fmt"
)

func f(array []int) []int {
    prev := array[0]
    newArray := make([]int, len(array))
    copy(newArray, array)
    for i := 1; i < len(array); i++ {
        if prev != array[i] {
            newArray[i] = array[i]
        } else {
            newArray = append(newArray[:i], newArray[i+1:]...)
            i--
        }
        prev = array[i]
    }
    return newArray
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 2, 3}), expected: []int{1, 2, 3} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
