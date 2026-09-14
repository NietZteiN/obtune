package f_test

import (
    "testing"
    "fmt"
)

func f(no []string) int {
    d := make(map[string]bool)
    for _, val := range no {
        d[val] = false
    }
    count := 0
    for range d {
        count++
    }
    return count
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"l", "f", "h", "g", "s", "b"}), expected: 6 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
