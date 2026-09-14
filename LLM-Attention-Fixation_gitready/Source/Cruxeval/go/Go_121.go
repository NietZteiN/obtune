package main

import (
    "fmt"
    "strings"
    "strconv"
    "testing"
)

func f(s string) string {
	nums := ""
	for _, char := range s {
		if char >= '0' && char <= '9' {
			nums += string(char)
		}
	}
	if nums == "" {
		return "none"
	}

	maxNum := 0
	numsSlice := strings.Split(nums, ",")
	for _, numStr := range numsSlice {
		num, _ := strconv.Atoi(numStr)
		if num > maxNum {
			maxNum = num
		}
	}
	return strconv.Itoa(maxNum)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("01,001"), expected: "1001" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
