package f_test

import (
    "testing"
    "fmt"
)

func f(key string, value string) []interface{} {
    dict_ := map[string]string{key: value}
    for k, v := range dict_ {
        return []interface{}{k, v}
    }
    return []interface{}{}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("read", "Is"), expected: []interface{}{"read", "Is"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
