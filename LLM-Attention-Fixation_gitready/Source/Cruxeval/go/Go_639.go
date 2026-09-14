package f_test

import (
    "testing"
    "fmt"
)

func f(perc string, full string) string {
    reply := ""
    i := 0
    for i < len(full) && i < len(perc) && perc[i] == full[i] {
        if perc[i] == full[i] {
            reply += "yes "
        } else {
            reply += "no "
        }
        i++
    }
    return reply
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("xabxfiwoexahxaxbxs", "xbabcabccb"), expected: "yes " },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
