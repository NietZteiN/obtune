package f_test

import (
    "testing"
    "fmt"
)

func f(values []int, item1 int, item2 int) []int {
    if values[len(values)-1] == item2 {
        if values[0] != item2 {
            values = append(values, values[0])
        }
    } else if values[len(values)-1] == item1 {
        if values[0] == item2 {
            values = append(values, values[0])
        }
    }
    return values
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 1}, 2, 3), expected: []int{1, 1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
