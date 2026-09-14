package f_test

import (
    "testing"
    "fmt"
)

func f(dict1 map[string]int, dict2 map[string]int) map[string]int {
    result := make(map[string]int)
    for key, value := range dict1 {
        result[key] = value
    }
    for key, value := range dict2 {
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
     { actual: candidate(map[string]int{"disface": 9, "cam": 7}, map[string]int{"mforce": 5}), expected: map[string]int{"disface": 9, "cam": 7, "mforce": 5} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
