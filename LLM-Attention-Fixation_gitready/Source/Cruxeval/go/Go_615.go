package f_test

import (
    "testing"
    "fmt"
)

func f(in_list []int, num int) int {
    in_list = append(in_list, num)
    maxVal := in_list[0]
    maxIndex := 0
    for i, val := range in_list[:len(in_list)-1] {
        if val > maxVal {
            maxVal = val
            maxIndex = i
        }
    }
    return maxIndex
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{-1, 12, -6, -2}, -1), expected: 1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
