package main

import (
    "fmt"
    "testing"
    "sort"
)

func f(num1 int, num2 int, num3 int) string {
	nums := []int{num1, num2, num3}
	sort.Ints(nums)
	return fmt.Sprintf("%d,%d,%d", nums[0], nums[1], nums[2])
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(6, 8, 8), expected: "6,8,8" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
