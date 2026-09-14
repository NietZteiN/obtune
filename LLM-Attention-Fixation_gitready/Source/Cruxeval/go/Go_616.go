package f_test

import (
	"strings"
	"testing"
	"fmt"
)

func f(body string) string {
	ls := strings.Split(body, "")
	dist := 0
	for i := 0; i < len(ls)-1; i++ {
		if i-2 >= 0 && ls[i-2][0] == '\t' {
			dist += (1 + strings.Count(ls[i-1], "\t")) * 3
		}
		ls[i] = "[" + ls[i] + "]"
	}
	joined := strings.Join(ls, "")
	return strings.Replace(joined, "\t", "    ", -1)
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("\n\ny\n"), expected: "[\n][\n][y]\n" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
