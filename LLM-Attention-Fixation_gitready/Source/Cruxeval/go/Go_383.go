package f_test

import (
    "testing"
    "fmt"
)

func f(text string, chars string) string {
    result := []rune(text)
    for index := len(result) - 3; index >= 0; index -= 2 {
        if string(result[index]) == chars {
            result = append(result[:index], result[index+2:]...)
        }
    }
    resultStr := string(result)
    if len(resultStr) > 0 && resultStr[len(resultStr)-1] == '.' {
        return resultStr[:len(resultStr)-1]
    }
    return resultStr
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("ellod!p.nkyp.exa.bi.y.hain", ".n.in.ha.y"), expected: "ellod!p.nkyp.exa.bi.y.hain" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
