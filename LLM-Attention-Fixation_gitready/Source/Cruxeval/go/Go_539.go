package f_test

import (
	"testing"
	"fmt"
)

func f(array []string) []string {
	array_copy := array

	for len(array_copy) < len(array) {
		array_copy = append(array_copy, "_")
	}

	return array_copy
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{}), expected: []string{""} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
