package f_test

import (
    "fmt"
    "strings"
    "testing"
)

func f(list_ []string, num int) []string {
    var temp []string
    for _, i := range list_ {
        i = fmt.Sprintf("%s,", i)
        i = strings.Repeat(i, num/2)
        temp = append(temp, i)
    }
    return temp
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"v"}, 1), expected: []string{""} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
