package f_test

import (
    "testing"
    "fmt"
)

func f(array []int, num int) []int {
    reverse := false
    if num < 0 {
        reverse = true
        num *= -1
    }
    reversedArray := make([]int, 0)
    for i := len(array) - 1; i >= 0; i-- {
        reversedArray = append(reversedArray, array[i])
    }
    newArray := make([]int, 0, len(array)*num)
    for i := 0; i < num; i++ {
        newArray = append(newArray, reversedArray...)
    }
    if reverse {
        reversedNewArray := make([]int, 0)
        for i := len(newArray) - 1; i >= 0; i-- {
            reversedNewArray = append(reversedNewArray, newArray[i])
        }
        return reversedNewArray
    }
    return newArray
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 2}, 1), expected: []int{2, 1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
