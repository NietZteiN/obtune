package f_test

import (
    "testing"
    "fmt"
)

func f(array []int, target int) int {
    count, i := 0, 1
    for j := 1; j < len(array); j++ {
        if array[j] > array[j-1] && array[j] <= target {
            count += i
        } else if array[j] <= array[j-1] {
            i = 1
        } else {
            i++
        }
    }
    return count
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 2, -1, 4}, 2), expected: 1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
