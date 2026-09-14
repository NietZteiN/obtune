package f_test

import (
    "testing"
    "fmt"
)

func f(num int) int {
    initial := []int{1}
    total := initial
    for i := 0; i < num; i++ {
        newTotal := make([]int, len(total)+1)
        newTotal[0] = 1
        for j := 1; j < len(newTotal)-1; j++ {
            newTotal[j] = total[j-1] + total[j]
        }
        newTotal[len(newTotal)-1] = total[len(total)-1]
        total = newTotal
        initial = append(initial, total[len(total)-1])
    }
    sum := 0
    for _, val := range initial {
        sum += val
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
     { actual: candidate(3), expected: 4 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
