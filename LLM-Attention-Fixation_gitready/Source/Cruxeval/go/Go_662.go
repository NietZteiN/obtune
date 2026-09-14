package main

import (
    "fmt"
    "testing"
    "sort"
)

func f(values []string) []string {
	names := []string{"Pete", "Linda", "Angela"}
	names = append(names, values...)
	sort.Strings(names)
	return names
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"Dan", "Joe", "Dusty"}), expected: []string{"Angela", "Dan", "Dusty", "Joe", "Linda", "Pete"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
