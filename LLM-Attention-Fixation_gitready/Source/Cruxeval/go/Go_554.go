package f_test

import (
    "testing"
    "fmt"
)

func f(arr []int) []int {
    reversedArr := make([]int, len(arr))
    for i, v := range arr {
        reversedArr[len(arr)-1-i] = v
    }
    return reversedArr
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{2, 0, 1, 9999, 3, -5}), expected: []int{-5, 3, 9999, 1, 0, 2} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
