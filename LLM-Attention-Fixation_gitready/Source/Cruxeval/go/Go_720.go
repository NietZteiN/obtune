package f_test

import (
	"testing"
	"fmt"
)

func f(items []string, item string) int {
	for items[len(items)-1] == item {
		items = items[:len(items)-1]
	}
	items = append(items, item)
	return len(items)
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"bfreratrrbdbzagbretaredtroefcoiqrrneaosf"}, "n"), expected: 2 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
