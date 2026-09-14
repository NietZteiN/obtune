package f_test

import (
    "fmt"
    "strings"
    "testing"
)

func f(seq []string, value string) map[string]string {
    roles := make(map[string]string)
    for _, s := range seq {
        roles[s] = "north"
    }
    if value != "" {
        keys := strings.Split(value, ", ")
        for _, key := range keys {
            roles[key] = ""
        }
    }
    return roles
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"wise king", "young king"}, ""), expected: map[string]string{"wise king": "north", "young king": "north"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
