package main

import (
    "fmt"
    "testing"
    "sort"
)

func f(d map[int]int) map[int]int {
	keys := make([]int, 0, len(d))
	for k := range d {
		keys = append(keys, k)
	}
	sort.Sort(sort.Reverse(sort.IntSlice(keys)))

	key1 := keys[0]
	val1 := d[key1]
	delete(d, key1)

	key2 := keys[1]
	val2 := d[key2]
	delete(d, key2)

	return map[int]int{key1: val1, key2: val2}
}

func main() {
	d := map[int]int{1: 10, 2: 20, 3: 30}
	result := f(d)
	fmt.Println(result)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]int{2: 3, 17: 3, 16: 6, 18: 6, 87: 7}), expected: map[int]int{87: 7, 18: 6} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
