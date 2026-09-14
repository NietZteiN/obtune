package f_test

import (
    "testing"
    "fmt"
)

func f(d map[string]string) map[string]string {
    for k := range d {
        delete(d, k)
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
     { actual: candidate(map[string]string{"a": "3", "b": "-1", "c": "Dum"}), expected: map[string]string{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
