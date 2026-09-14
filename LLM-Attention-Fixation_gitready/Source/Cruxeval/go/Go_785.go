package f_test

import (
    "testing"
    "fmt"
    "strconv"
    "strings"
)

func f(n int) string {
    streak := ""
    for _, c := range strconv.Itoa(n) {
        count, _ := strconv.Atoi(string(c))
        streak += string(c) + strings.Repeat(" ", count)
    }
    return streak
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(1), expected: "1 " },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
