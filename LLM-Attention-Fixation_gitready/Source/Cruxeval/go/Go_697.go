package f_test

import (
    "testing"
    "fmt"
)

func f(s string, sep string) []interface{} {
    sep_index := -1
    for i := 0; i < len(s)-len(sep)+1; i++ {
        if s[i:i+len(sep)] == sep {
            sep_index = i
            break
        }
    }
    if sep_index == -1 {
        return []interface{}{s, "", ""}
    }
    prefix := s[:sep_index]
    middle := s[sep_index : sep_index+len(sep)]
    rightStr := s[sep_index+len(sep):]
    return []interface{}{prefix, middle, rightStr}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("not it", ""), expected: []interface{}{"", "", "not it"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
