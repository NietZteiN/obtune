package main

import (
    "fmt"
    "testing"
)

func f(start int, end int, interval int) int {
	steps := make([]int, 0)
	for i := start; i <= end; i += interval {
		steps = append(steps, i)
	}
	if contains(steps, 1) {
		steps[len(steps)-1] = end + 1
	}
	return len(steps)
}

func contains(arr []int, target int) bool {
	for _, val := range arr {
		if val == target {
			return true
		}
	}
	return false
}

func main() {
	start := 1
	end := 10
	interval := 2
	result := f(start, end, interval)
	fmt.Println(result)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(3, 10, 1), expected: 8 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
