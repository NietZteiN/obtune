package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int) int {
    newNums := make([]int, len(nums))
    copy(newNums, nums)

    for i := 0; i < len(newNums); i++ {
        if newNums[i] % 2 != 0 {
            newNums = append(newNums[:i], newNums[i+1:]...)
            i--
        }
    }

    sum := 0
    for _, num := range newNums {
        sum += num
    }

    return sum
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{11, 21, 0, 11}), expected: 0 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
