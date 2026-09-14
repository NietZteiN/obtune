package f_test

import (
    "fmt"
    "strings"
    "testing"
)

func f(s string) map[string]int {
    count := make(map[string]int)

    for _, i := range s {
        if i >= 'a' && i <= 'z' {
            count[string(i)] = strings.Count(s, strings.ToLower(string(i))) + count[strings.ToLower(string(i))]
        } else {
            count[strings.ToLower(string(i))] = strings.Count(s, strings.ToUpper(string(i))) + count[strings.ToLower(string(i))]
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
     { actual: candidate("FSA"), expected: map[string]int{"f": 1, "s": 1, "a": 1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
