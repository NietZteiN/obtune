package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int) []int {
    filteredNums := make([]int, 0)
    for _, y := range nums {
        if y > 0 {
            filteredNums = append(filteredNums, y)
        }
    }
    
    if len(filteredNums) <= 3 {
        return filteredNums
    }
    
    reverseNums := make([]int, len(filteredNums))
    for i, j := 0, len(filteredNums)-1; i < len(filteredNums); i, j = i+1, j-1 {
        reverseNums[i] = filteredNums[j]
    }
    
    half := len(filteredNums) / 2
    result := append(reverseNums[:half], make([]int, 5)...)
    result = append(result, reverseNums[half:]...)
    
    return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{10, 3, 2, 2, 6, 0}), expected: []int{6, 2, 0, 0, 0, 0, 0, 2, 3, 10} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
