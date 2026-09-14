package f_test

import (
    "testing"
    "fmt"
    "unicode"
)

func f(text string) []interface{} {
    ws := 0
    for _, s := range text {
        if unicode.IsSpace(s) {
            ws += 1
        }
    }
    return []interface{}{ws, len(text)}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("jcle oq wsnibktxpiozyxmopqkfnrfjds"), expected: []interface{}{2, 34} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
