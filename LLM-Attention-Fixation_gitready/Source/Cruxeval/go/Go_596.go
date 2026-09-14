package main

import (
    "fmt"
    "testing"
    "sort"
)

func f(txt []string, alpha string) []string {
	sort.Strings(txt)
	for i, val := range txt {
		if val == alpha {
			if i%2 == 0 {
				reverse(txt)
			}
			break
		}
	}
	return txt
}

func reverse(s []string) {
	for i := 0; i < len(s)/2; i++ {
		j := len(s) - i - 1
		s[i], s[j] = s[j], s[i]
	}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"8", "9", "7", "4", "3", "2"}, "9"), expected: []string{"2", "3", "4", "7", "8", "9"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
