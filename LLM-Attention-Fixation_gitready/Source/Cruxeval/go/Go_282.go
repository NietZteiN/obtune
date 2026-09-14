package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(s1 string, s2 string) int {
    position := 1
    count := 0
    for position > 0 {
        position = strings.Index(s1[position:], s2)
        if position != -1 {
            position += len(s2)
        }
        count += 1
    }
    return count
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("xinyyexyxx", "xx"), expected: 2 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
