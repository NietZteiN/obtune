package f_test

import (
    "testing"
    "fmt"
)

func f(d map[string]int) []interface{} {
    var result []interface{}
    i := 0
    for k, v := range d {
        if i < 2 {
            result = append(result, []interface{}{k, v})
            i++
        } else {
            break
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
     { actual: candidate(map[string]int{"a": 123, "b": 456, "c": 789}), expected: []interface{}{[]interface{}{"a", 123}, []interface{}{"b", 456}} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
