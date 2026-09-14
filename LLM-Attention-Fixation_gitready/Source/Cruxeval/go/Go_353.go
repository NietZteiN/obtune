package f_test

import (
    "testing"
    "fmt"
)

func f(x []int) int {
    if len(x) == 0 {
        return -1
    } else {
        cache := make(map[int]int)
        for _, item := range x {
            if val, ok := cache[item]; ok {
                cache[item] = val + 1
            } else {
                cache[item] = 1
            }
        }
        maxCount := 0
        for _, count := range cache {
            if count > maxCount {
                maxCount = count
            }
        }
        return maxCount
    }
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 0, 2, 2, 0, 0, 0, 1}), expected: 4 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
