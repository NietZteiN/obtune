package f_test

import (
	"testing"
	"fmt"
	"sort"
)

func f(strings []string, substr string) []string {
	list := make([]string, 0)
	for _, s := range strings {
		if len(s) >= len(substr) && s[:len(substr)] == substr {
			list = append(list, s)
		}
	}
	sort.Slice(list, func(i, j int) bool { return len(list[i]) < len(list[j]) })
	return list
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"condor", "eyes", "gay", "isa"}, "d"), expected: []string{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
