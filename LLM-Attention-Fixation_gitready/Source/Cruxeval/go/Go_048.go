package f_test

import (
    "testing"
    "fmt"
)

func f(names []string) string {
    if len(names) == 0 {
        return ""
    }
    smallest := names[0]
    for _, name := range names[1:] {
        if name < smallest {
            smallest = name
        }
    }
    var idx int
    for i, name := range names {
        if name == smallest {
            idx = i
            break
        }
    }
    names = append(names[:idx], names[idx+1:]...)
    return smallest
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{}), expected: "" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
