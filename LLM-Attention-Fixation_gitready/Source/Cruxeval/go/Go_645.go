package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int, target int) int {
    zeroCount := 0
    targetCount := 0

    for _, num := range nums {
        if num == 0 {
            zeroCount++
        }
        if num == target {
            targetCount++
        }
    }

    if zeroCount > 0 {
        return 0
    } else if targetCount < 3 {
        return 1
    } else {
        for i, num := range nums {
            if num == target {
                return i
            }
        }
    }

    return -1 // default return value if target is not found
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 1, 1, 2}, 3), expected: 1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
