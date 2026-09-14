package f_test

import (
    "testing"
    "fmt"
)

func f(nums map[string]string) map[string]int {
    newDict := make(map[string]int)
    for k, v := range nums {
        newDict[k] = len(v)
    }
    return newDict
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[string]string{}), expected: map[string]int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
