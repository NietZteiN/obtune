package f_test

import (
    "testing"
    "fmt"
)

func f(single_digit int) []int {
    var result []int
    for c := 1; c <= 10; c++ {
        if c != single_digit {
            result = append(result, c)
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
     { actual: candidate(5), expected: []int{1, 2, 3, 4, 6, 7, 8, 9, 10} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
