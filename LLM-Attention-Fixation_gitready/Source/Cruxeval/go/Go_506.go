package f_test

import (
    "testing"
    "fmt"
)

func f(n int) string {
    p := ""
    if n % 2 == 1 {
        p += "sn"
    } else {
        return fmt.Sprintf("%d", n*n)
    }
    for x := 1; x <= n; x++ {
        if x % 2 == 0 {
            p += "to"
        } else {
            p += "ts"
        }
    }
    return p
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(1), expected: "snts" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
