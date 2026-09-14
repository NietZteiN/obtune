import std.math;
import std.typecons;
import std.conv;
import std.string;

string[] f(string[] nums) 
{
    int width = to!int(nums[0]);
    string[] formattedNums;
    foreach (i, val; nums[1..$])
    {
        formattedNums ~= format("%0*d", width, to!int(val));
    }
    return formattedNums;
}
unittest
{
    alias candidate = f;

    assert(candidate(["1", "2", "2", "44", "0", "7", "20257"]) == ["2", "2", "44", "0", "7", "20257"]);
}
void main(){}
