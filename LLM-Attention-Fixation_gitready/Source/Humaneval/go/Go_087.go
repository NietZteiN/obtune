import (
    "sort"
)

// You are given a 2 dimensional data, as a nested lists,
// which is similar to matrix, however, unlike matrices,
// each row may contain a different number of columns.
// Given lst, and integer x, find integers x in the list,
// and return list of tuples, [(x1, y1), (x2, y2) ...] such that
// each tuple is a coordinate - (row, columns), starting with 0.
// Sort coordinates initially by rows in ascending order.
// Also, sort coordinates of the row by columns in descending order.
// 
// Examples:
// GetRow([
// [1,2,3,4,5,6],
// [1,2,3,4,1,6],
// [1,2,3,4,5,1]
// ], 1) == [(0, 0), (1, 4), (1, 0), (2, 5), (2, 0)]
// GetRow([], 1) == []
// GetRow([[], [1], [1, 2, 3]], 3) == [(2, 2)]
func GetRow(lst [][]int, x int) [][2]int {

    coords := make([][2]int, 0)
    for i, row := range lst {
        for j, item := range row {
            if item == x {
                coords = append(coords, [2]int{i, j})
            }
        }
    }
    sort.Slice(coords, func(i, j int) bool {
        if coords[i][0] == coords[j][0] {
            return coords[i][1] > coords[j][1]
        }
        return coords[i][0] < coords[j][0]
    })

    return coords
}

func TestGetRow(t *testing.T) {
    assert := assert.New(t)
    assert.Equal([][2]int{{0, 0}, {1, 4}, {1, 0}, {2, 5}, {2, 0}}, GetRow([][]int{
        {1, 2, 3, 4, 5, 6},
        {1, 2, 3, 4, 1, 6},
        {1, 2, 3, 4, 5, 1},
    }, 1))
    assert.Equal([][2]int{{0, 1}, {1, 1}, {2, 1}, {3, 1}, {4, 1}, {5, 1}}, GetRow([][]int{
        {1, 2, 3, 4, 5, 6},
        {1, 2, 3, 4, 5, 6},
        {1, 2, 3, 4, 5, 6},
        {1, 2, 3, 4, 5, 6},
        {1, 2, 3, 4, 5, 6},
        {1, 2, 3, 4, 5, 6},
    }, 2))
    assert.Equal([][2]int{{0, 0}, {1, 0}, {2, 1}, {2, 0}, {3, 2}, {3, 0}, {4, 3}, {4, 0}, {5, 4}, {5, 0}, {6, 5}, {6, 0}}, GetRow([][]int{
        {1, 2, 3, 4, 5, 6},
        {1, 2, 3, 4, 5, 6},
        {1, 1, 3, 4, 5, 6},
        {1, 2, 1, 4, 5, 6},
        {1, 2, 3, 1, 5, 6},
        {1, 2, 3, 4, 1, 6},
        {1, 2, 3, 4, 5, 1},
    }, 1))
    assert.Equal([][2]int{}, GetRow([][]int{{}}, 1))
    assert.Equal([][2]int{}, GetRow([][]int{{1}}, 2))
    assert.Equal([][2]int{{2, 2}}, GetRow([][]int{{}, {1}, {1, 2, 3}}, 3))
}
