package f_test

import (
    "testing"
    "fmt"
)

func f(strings []string) map[string]int {
    occurances := make(map[string]int)
    for _, str := range strings {
        if _, ok := occurances[str]; !ok {
            occurances[str] = 0
            for _, s := range strings {
                if s == str {
                    occurances[str]++
                }
            }
        }
    }
    return occurances
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"La", "Q", "9", "La", "La"}), expected: map[string]int{"La": 3, "Q": 1, "9": 1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
