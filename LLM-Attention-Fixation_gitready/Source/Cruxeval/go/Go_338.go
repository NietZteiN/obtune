package f_test

import (
    "testing"
    "fmt"
)

func f(my_dict map[string]int) map[int]string {
    result := make(map[int]string)
    for k, v := range my_dict {
        result[v] = k
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
     { actual: candidate(map[string]int{"a": 1, "b": 2, "c": 3, "d": 2}), expected: map[int]string{1: "a", 2: "d", 3: "c"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
