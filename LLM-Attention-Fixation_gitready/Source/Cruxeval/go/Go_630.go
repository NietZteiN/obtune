package f_test

import (
    "testing"
    "fmt"
)

func f(original map[int]int, myString map[int]int) map[int]int {
    temp := make(map[int]int, len(original))
    for k, v := range original {
        temp[k] = v
    }
    for a, b := range myString {
        temp[b] = a
    }
    return temp
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]int{1: -9, 0: -7}, map[int]int{1: 2, 0: 3}), expected: map[int]int{1: -9, 0: -7, 2: 1, 3: 0} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
