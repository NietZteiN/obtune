package f_test

import (
    "testing"
    "fmt"
)

func f(mylist []int) bool {
    revl := make([]int, len(mylist))
    copy(revl, mylist)
    for i, j := 0, len(mylist)-1; i < j; i, j = i+1, j-1 {
        revl[i], revl[j] = revl[j], revl[i]
    }
    
    for i := range mylist {
        for j := range mylist {
            if mylist[i] > mylist[j] {
                mylist[i], mylist[j] = mylist[j], mylist[i]
            }
        }
    }
    
    return fmt.Sprintf("%v", mylist) == fmt.Sprintf("%v", revl)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{5, 8}), expected: true },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
