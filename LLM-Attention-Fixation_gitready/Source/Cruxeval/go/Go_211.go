package f_test

import (
    "testing"
    "fmt"
)

func f(s string) int {
    count := 0
    for i := 0; i < len(s); i++ {
        found := false
        for j := 0; j < len(s); j++ {
            if s[i] == s[j] && i != j {
                found = true
                break
            }
        }
        if found {
            count++
        }
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
     { actual: candidate("abca dea ead"), expected: 10 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
