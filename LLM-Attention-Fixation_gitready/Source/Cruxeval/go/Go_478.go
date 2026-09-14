package f_test

import (
    "testing"
    "fmt"
)

func f(sb string) map[string]int {
    d := make(map[string]int)
    for _, s := range sb {
        d[string(s)] = d[string(s)] + 1
    }
    return d
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("meow meow"), expected: map[string]int{"m": 2, "e": 2, "o": 2, "w": 2, " ": 1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
