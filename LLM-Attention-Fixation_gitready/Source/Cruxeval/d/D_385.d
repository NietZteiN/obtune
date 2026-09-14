import std.math;
import std.typecons;
import std.array;
import std.algorithm;

long[] f(long[] lst) 
{
    long[] new_list;
    long i = 0;
    while (i < lst.length)
    {
        if (lst.count(lst[i]) > 1)
        {
            new_list ~= lst[i];
            if (new_list.length == 3)
            {
                return new_list;
            }
        }
        i++;
    }
    return new_list;
}
unittest
{
    alias candidate = f;

    assert(candidate([0L, 2L, 1L, 2L, 6L, 2L, 6L, 3L, 0L]) == [0L, 2L, 2L]);
}
void main(){}
