package f_test

import (
    "strings"
    "testing"
    "fmt"
)

func f(s string) string {
    d := strings.Split(s, "ar")
    if len(d) == 1 {
        return s
    }
    return fmt.Sprintf("%s ar %s", strings.Join(d[:len(d)-1], "ar"), d[len(d)-1])
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("xxxarmmarxx"), expected: "xxxarmm ar xx" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
