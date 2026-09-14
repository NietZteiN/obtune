package f_test

import (
    "testing"
    "fmt"
)

func f(array []int, lst []int) []int {
    array = append(array, lst...)
    var evenNumbers []int
    for _, e := range array {
        if e % 2 == 0 {
            evenNumbers = append(evenNumbers, e)
        }
    }
    result := []int{}
    for _, e := range array {
        if e >= 10 {
            result = append(result, e)
        }
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
     { actual: candidate([]int{2, 15}, []int{15, 1}), expected: []int{15, 15} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
