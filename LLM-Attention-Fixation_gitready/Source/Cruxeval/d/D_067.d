import std.math;
import std.typecons;
import std.algorithm;
import std.format;

string f(long num1, long num2, long num3) 
{
    long[] nums = [num1, num2, num3];
    nums.sort();
    return format("%s,%s,%s", nums[0], nums[1], nums[2]);
}
unittest
{
    alias candidate = f;

    assert(candidate(6L, 8L, 8L) == "6,8,8");
}
void main(){}
