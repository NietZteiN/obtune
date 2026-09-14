package f_test

import (
    "testing"
    "fmt"
)

func f(album_sales []int) int {
    for len(album_sales) != 1 {
        album_sales = append(album_sales, album_sales[0])
        album_sales = album_sales[1:]
    }
    return album_sales[0]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{6}), expected: 6 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
