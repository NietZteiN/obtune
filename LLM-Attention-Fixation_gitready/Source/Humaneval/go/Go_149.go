import (
    "sort"
)

// Write a function that accepts a list of strings as a parameter,
// deletes the strings that have odd lengths from it,
// and returns the resulted list with a sorted order,
// The list is always a list of strings and never an array of numbers,
// and it may contain duplicates.
// The order of the list should be ascending by length of each word, and you
// should return the list sorted by that rule.
// If two words have the same length, sort the list alphabetically.
// The function should return a list of strings in sorted order.
// You may assume that all words will have the same length.
// For example:
// assert list_sort(["aa", "a", "aaa"]) => ["aa"]
// assert list_sort(["ab", "a", "aaa", "cd"]) => ["ab", "cd"]
func SortedListSum(lst []string) []string {

    sort.SliceStable(lst, func(i, j int) bool {
        return lst[i] < lst[j]
    })
    new_lst := make([]string, 0)
    for _, i := range lst {
        if len(i)&1==0 {
            new_lst = append(new_lst, i)
        }
    }
    sort.SliceStable(new_lst, func(i, j int) bool {
        return len(new_lst[i]) < len(new_lst[j])
    })
    return new_lst
}

func TestSortedListSum(t *testing.T) {
    assert := assert.New(t)
    assert.Equal([]string{"aa"}, SortedListSum([]string{"aa", "a", "aaa"}))
    assert.Equal([]string{"AI", "asdf", "school"}, SortedListSum([]string{"school", "AI", "asdf", "b"}))
    assert.Equal([]string{}, SortedListSum([]string{"d", "b", "c", "a"}))
    assert.Equal([]string{"abcd", "dcba"}, SortedListSum([]string{"d", "dcba", "abcd", "a"}))
    assert.Equal([]string{"AI", "ai", "au"}, SortedListSum([]string{"AI", "ai", "au"}))
    assert.Equal([]string{}, SortedListSum([]string{"a", "b", "b", "c", "c", "a"}))
    assert.Equal([]string{"cc", "dd", "aaaa", "bbbb"}, SortedListSum([]string{"aaaa", "bbbb", "dd", "cc"}))
}
