import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] items) 
{
    long[] odd_positioned;
    while (items.length > 0)
    {
        auto min_index = findMin(items);
        items = items[0 .. min_index] ~ items[min_index + 1 .. $];
        auto item = items[0];
        items = items[1 .. $];
        odd_positioned ~= item;
    }
    return odd_positioned;
}

size_t findMin(long[] items)
{
    size_t minIndex = 0;
    foreach(i, item; items)
    {
        if(item < items[minIndex])
            minIndex = i;
    }
    return minIndex;
}

unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 3L, 4L, 5L, 6L, 7L, 8L]) == [2L, 4L, 6L, 8L]);
}
void main(){}
