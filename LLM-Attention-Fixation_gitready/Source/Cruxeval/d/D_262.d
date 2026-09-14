import std.math;
import std.typecons;
import std.array;

string f(long[] nums) 
{
    long count = nums.length;
    immutable score = [0: "F", 1: "E", 2: "D", 3: "C", 4: "B", 5: "A", 6: ""];
    string[] result;
    foreach (i; 0 .. count) {
        result ~= score[cast(int)nums[i]];
    }
    return result.join("");
}
unittest
{
    alias candidate = f;

    assert(candidate([4L, 5L]) == "BA");
}
void main(){}
