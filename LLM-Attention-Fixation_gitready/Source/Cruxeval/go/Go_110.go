package f_test

import (
    "testing"
    "fmt"
)

func f(text string) int {
    a := []string{""}
    var b string
    for _, i := range text {
        if string(i) != " " {
            a = append(a, b)
            b = ""
        } else {
            b += string(i)
        }
    }
    return len(a)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("       "), expected: 1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
