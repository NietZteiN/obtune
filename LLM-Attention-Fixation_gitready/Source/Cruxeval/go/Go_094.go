package f_test

import (
    "testing"
    "fmt"
)

func f(a map[string]int, b map[string]int) map[string]int {
    result := make(map[string]int)
    for key, value := range a {
        result[key] = value
    }
    for key, value := range b {
        result[key] = value
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
     { actual: candidate(map[string]int{"w": 5, "wi": 10}, map[string]int{"w": 3}), expected: map[string]int{"w": 3, "wi": 10} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
