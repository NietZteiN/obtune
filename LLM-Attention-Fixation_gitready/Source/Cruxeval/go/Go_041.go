package f_test

import (
    "testing"
    "fmt"
)

func f(array []int, values []int) []int {
    reversedArray := make([]int, len(array))
    copy(reversedArray, array)
    for i, j := 0, len(reversedArray)-1; i < j; i, j = i+1, j-1 {
        reversedArray[i], reversedArray[j] = reversedArray[j], reversedArray[i]
    }

    for _, value := range values {
        middleIndex := len(reversedArray) / 2
        reversedArray = append(reversedArray[:middleIndex], append([]int{value}, reversedArray[middleIndex:]...)...)
    }

    reversedArrayCopy := make([]int, len(reversedArray))
    copy(reversedArrayCopy, reversedArray)
    for i, j := 0, len(reversedArrayCopy)-1; i < j; i, j = i+1, j-1 {
        reversedArrayCopy[i], reversedArrayCopy[j] = reversedArrayCopy[j], reversedArrayCopy[i]
    }

    return reversedArrayCopy
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{58}, []int{21, 92}), expected: []int{58, 92, 21} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
