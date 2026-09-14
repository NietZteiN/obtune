package f_test

import (
    "testing"
    "fmt"
)

func f(dict map[int]string) []int {
    var evenKeys []int
    for key := range dict {
        if key%2 == 0 {
            evenKeys = append(evenKeys, key)
        }
    }
    return evenKeys
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]string{4: "a"}), expected: []int{4} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
