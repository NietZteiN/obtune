package f_test

import (
    "testing"
    "fmt"
    "unicode"
)

func f(myString string) string {
    for len(myString) > 0 {
        if unicode.IsLetter(rune(myString[len(myString)-1])) {
            return myString
        }
        myString = myString[:len(myString)-1]
    }
    return myString
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("--4/0-209"), expected: "" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
