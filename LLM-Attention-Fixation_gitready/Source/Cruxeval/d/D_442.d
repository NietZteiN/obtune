import std.math;
import std.typecons;
long[] f(long[] lst) 
{
    long[] res;
    foreach (num; lst) {
        if (num % 2 == 0) {
            res ~= num;
        }
    }
    
    return lst.dup;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 3L, 4L]) == [1L, 2L, 3L, 4L]);
}
void main(){}
