package f_test

import (
    "testing"
    "fmt"
)

func f(dic map[int]string) map[string]int {
    dic2 := make(map[string]int)
    for key, value := range dic {
        dic2[value] = key
    }
    return dic2
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]string{-1: "a", 0: "b", 1: "c"}), expected: map[string]int{"a": -1, "b": 0, "c": 1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
