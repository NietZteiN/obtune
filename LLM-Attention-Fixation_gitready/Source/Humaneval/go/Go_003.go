
// You're given a list of deposit and withdrawal operations on a bank account that starts with
// zero balance. Your task is to detect if at any point the balance of account fallls below zero, and
// at that point function should return true. Otherwise it should return false.
// >>> BelowZero([1, 2, 3])
// false
// >>> BelowZero([1, 2, -4, 5])
// true
func BelowZero(operations []int) bool {

    balance := 0
    for _, op := range operations {
        balance += op
        if balance < 0 {
            return true
        }
    }
    return false
}

func TestBelowZero(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(false, BelowZero([]int{}))
    assert.Equal(false, BelowZero([]int{1, 2, -3, 1, 2, -3}))
    assert.Equal(true, BelowZero([]int{1, 2, -4, 5, 6}))
    assert.Equal(false, BelowZero([]int{1, -1, 2, -2, 5, -5, 4, -4}))
    assert.Equal(true, BelowZero([]int{1, -1, 2, -2, 5, -5, 4, -5}))
    assert.Equal(true, BelowZero([]int{1, -2, 2, -2, 5, -5, 4, -4}))
}
