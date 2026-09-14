package f_test

import (
	"testing"
	"fmt"
)

func f(nums []int, fill string) map[int]string {
	ans := make(map[int]string, len(nums))
	for _, num := range nums {
		ans[num] = fill
	}
	return ans
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{0, 1, 1, 2}, "abcca"), expected: map[int]string{0: "abcca", 1: "abcca", 2: "abcca"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
