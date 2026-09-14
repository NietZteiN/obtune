package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(dct map[string]string) map[string]string {
	values := make([]string, 0, len(dct))
	for _, v := range dct {
		values = append(values, v)
	}

	result := make(map[string]string)
	for _, value := range values {
		item := value[:strings.Index(value, ".")] + "@pinc.uk"
		result[value] = item
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
     { actual: candidate(map[string]string{}), expected: map[string]string{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
