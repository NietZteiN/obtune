package main

import (
    "fmt"
    "testing"
    "sort"
)

func f(values []string, value int) map[string]int {
	newDict := make(map[string]int)
	for _, v := range values {
		newDict[v] = value
	}
	sortedValues := make([]byte, 0)
	for _, v := range values {
		sortedValues = append(sortedValues, v...)
	}
	sort.Slice(sortedValues, func(i, j int) bool {
		return sortedValues[i] < sortedValues[j]
	})
	newDict[string(sortedValues)] = value * 3
	return newDict
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"0", "3"}, 117), expected: map[string]int{"0": 117, "3": 117, "03": 351} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
