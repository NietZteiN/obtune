package f_test

import (
    "testing"
    "fmt"
)

func f(d map[string]int) []interface{} {
    var key string
    i := len(d) - 1
    for k := range d {
        if i == 0 {
            key = k
            break
        }
        i--
    }
    delete(d, key)
    return []interface{}{key, d}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[string]int{"e": 1, "d": 2, "c": 3}), expected: []interface{}{"c", map[string]int{"e": 1, "d": 2}} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
