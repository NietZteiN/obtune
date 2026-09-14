package f_test

import (
    "testing"
    "fmt"
)

func f(L []int, m int, start int, step int) []int {
    L = append(L[:start], append([]int{m}, L[start:]...)...)
    for x := start - 1; x > 0; x -= step {
        start -= 1
        index := findIndex(L, m)
        L = append(L[:start], append([]int{L[index-1]}, L[start:]...)...)
        L = append(L[:index], L[index+1:]...)
    }
    return L
}

func findIndex(arr []int, value int) int {
    for i, v := range arr {
        if v == value {
            return i
        }
    }
    return -1
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 2, 7, 9}, 3, 3, 2), expected: []int{1, 2, 7, 3, 9} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
