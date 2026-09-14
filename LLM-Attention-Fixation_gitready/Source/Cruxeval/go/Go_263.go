package f_test

import (
    "testing"
    "fmt"
)

func f(base []string, delta [][]string) []string {
    for j := 0; j < len(delta); j++ {
        for i := 0; i < len(base); i++ {
            if base[i] == delta[j][0] && delta[j][1] != base[i] {
                base[i] = delta[j][1]
            }
        }
    }
    return base
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"gloss", "banana", "barn", "lawn"}, [][]string{}), expected: []string{"gloss", "banana", "barn", "lawn"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
