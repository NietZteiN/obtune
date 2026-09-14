package f_test

import (
    "testing"
    "fmt"
)

func f(lst []int, start int, end int) int {
    count := 0
    for i := start; i < end; i++ {
        for j := i; j < end; j++ {
            if lst[i] != lst[j] {
                count++
            }
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
     { actual: candidate([]int{1, 2, 4, 3, 2, 1}, 0, 3), expected: 3 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
