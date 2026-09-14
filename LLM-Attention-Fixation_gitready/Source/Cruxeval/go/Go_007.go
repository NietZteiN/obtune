package f_test

import (
    "testing"
    "fmt"
)

func f(list []int) []int {
    original := make([]int, len(list))
    copy(original, list)
    for len(list) > 1 {
        list = list[:len(list)-1]
        for i := range list {
            list = append(list[:i], list[i+1:]...)
        }
    }
    list = original
    if len(list) > 0 {
        list = list[1:]
    }
    return list
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{}), expected: []int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
