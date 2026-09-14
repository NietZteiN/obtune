package f_test

import (
    "testing"
    "fmt"
)

func f(myString string, code string) string {
    t := ""
    defer func() {
        if r := recover(); r != nil {
            t = ""
        }
    }()
    
    t = myString
    return t
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("towaru", "UTF-8"), expected: "towaru" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
