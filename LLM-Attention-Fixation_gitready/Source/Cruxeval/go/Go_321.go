package f_test

import (
    "testing"
    "fmt"
)

func f(update map[string]int, starting map[string]int) map[string]int {
    d := make(map[string]int)
    for k, v := range starting {
        d[k] = v
    }
    for k, v := range update {
        if val, ok := d[k]; ok {
            d[k] = val + v
        } else {
            d[k] = v
        }
    }
    return d
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[string]int{}, map[string]int{"desciduous": 2}), expected: map[string]int{"desciduous": 2} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
