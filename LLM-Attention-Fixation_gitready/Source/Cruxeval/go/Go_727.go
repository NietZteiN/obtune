package main

import (
    "fmt"
    "strings"
    "testing"
    "sort"
)

func f(numbers []string, prefix string) []string {
	var result []string

	for _, n := range numbers {
		if len(n) > len(prefix) && strings.HasPrefix(n, prefix) {
			result = append(result, n[len(prefix):])
		} else {
			result = append(result, n)
		}
	}

	sort.Strings(result)

	return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"ix", "dxh", "snegi", "wiubvu"}, ""), expected: []string{"dxh", "ix", "snegi", "wiubvu"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
