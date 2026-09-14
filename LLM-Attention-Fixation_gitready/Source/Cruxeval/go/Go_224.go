package f_test

import (
    "testing"
    "fmt"
)

func f(array []string, value int) map[string]int {
    result := make(map[string]int)
    for i := len(array) - 1; i >= 1; i-- {
        array = array[:i]
        odd := make(map[string]int)
        odd[array[i]] = value
        result[array[i]] = value
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
     { actual: candidate([]string{"23"}, 123), expected: map[string]int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
