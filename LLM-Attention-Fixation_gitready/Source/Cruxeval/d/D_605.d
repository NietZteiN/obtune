import std.math;
import std.typecons;
string f(long[] nums) 
{
    nums.length = 0;
    return "quack";
}
unittest
{
    alias candidate = f;

    assert(candidate([2L, 5L, 1L, 7L, 9L, 3L]) == "quack");
}
void main(){}
