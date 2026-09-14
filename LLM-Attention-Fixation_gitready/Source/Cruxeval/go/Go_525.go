package f_test

import (
    "testing"
    "fmt"
)

func f(c map[string]int, st int, ed int) []interface{} {
    d := make(map[int]string)
    var a, b string
    for x, y := range c {
        d[y] = x
        if y == st {
            a = x
        }
        if y == ed {
            b = x
        }
    }
    w := d[st]
    if a > b {
        return []interface{}{w, b}
    } else {
        return []interface{}{b, w}
    }
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[string]int{"TEXT": 7, "CODE": 3}, 7, 3), expected: []interface{}{"TEXT", "CODE"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
