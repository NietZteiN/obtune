package f_test

import (
    "testing"
    "fmt"
)

func f(text string) []int {
    occ := make(map[rune]int)
    for _, ch := range text {
        name := map[rune]rune{'a': 'b', 'b': 'c', 'c': 'd', 'd': 'e', 'e': 'f'}
        nameCh := name[ch]
        if nameCh == 0 {
            nameCh = ch
        }
        occ[nameCh] = occ[nameCh] + 1
    }
    
    result := []int{}
    for _, x := range occ {
        result = append(result, x)
    }
    
    return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("URW rNB"), expected: []int{1, 1, 1, 1, 1, 1, 1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
