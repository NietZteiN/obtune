package f_test

import (
    "testing"
    "fmt"
)

func f(phrase string) string {
    result := ""
    for _, i := range phrase {
        if i < 'a' || i > 'z' {
            result += string(i)
        }
    }
    return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("serjgpoDFdbcA."), expected: "DFA." },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
