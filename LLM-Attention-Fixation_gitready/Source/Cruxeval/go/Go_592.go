package f_test

import (
    "testing"
    "fmt"
)

func f(numbers []int) []int {
    new_numbers := make([]int, 0)
    for i := len(numbers) - 1; i >= 0; i-- {
        new_numbers = append(new_numbers, numbers[i])
    }
    return new_numbers
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{11, 3}), expected: []int{3, 11} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
