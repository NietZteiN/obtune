package f_test

import (
    "testing"
    "fmt"
)

func f(n int, m int, num int) int {
    xList := make([]int, m-n+1)
    for i := n; i <= m; i++ {
        xList[i-n] = i
    }
    
    j := 0
    for {
        j = (j + num) % len(xList)
        if xList[j]%2 == 0 {
            return xList[j]
        }
    }
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(46, 48, 21), expected: 46 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
