import std.math;
import std.typecons;
long f(long[] nums) 
{
    long[] filteredNums;
    foreach (num; nums) {
        if (num % 2 == 0) {
            filteredNums ~= num;
        }
    }
    
    long sum = 0;
    foreach (num; filteredNums) {
        sum += num;
    }
    
    return sum;
}
unittest
{
    alias candidate = f;

    assert(candidate([11L, 21L, 0L, 11L]) == 0L);
}
void main(){}
