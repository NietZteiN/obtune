package f_test

import (
    "testing"
    "fmt"
)

func f(query string, base map[string]int) int {
    netSum := 0
    for key, val := range base {
        if string(key[0]) == query && len(key) == 3 {
            netSum -= val
        } else if string(key[len(key)-1]) == query && len(key) == 3 {
            netSum += val
        }
    }
    return netSum
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("a", map[string]int{}), expected: 0 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
